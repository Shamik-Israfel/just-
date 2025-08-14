import numpy as np
from sklearn.neighbors import NearestNeighbors
import joblib
from flask import Flask, jsonify, request, send_file
from supabase import create_client
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import tempfile

load_dotenv()

app = Flask(__name__)

# Configure Supabase
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Email configuration
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = os.getenv('EMAIL_PORT', 587)
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')

def train_model(crop_data):
    # Enhanced feature engineering
    features = []
    for crop in crop_data:
        features.append([
            len(crop['name']),        # Name length
            float(crop['price']),     # Price
            float(crop['quantity']),  # Quantity
            1 if 'vegetable' in crop['type'].lower() else 0,
            1 if 'fruit' in crop['type'].lower() else 0,
            1 if 'rice' in crop['type'].lower() else 0,
            float(crop['price']) / float(crop['quantity'])  # Price per unit
        ])
    
    X = np.array(features)
    model = NearestNeighbors(n_neighbors=5, metric='cosine', algorithm='brute')
    model.fit(X)
    joblib.dump(model, 'crop_model.joblib')
    return model

def get_ai_recommendations(cart_items, supabase):
    try:
        all_crops = supabase.table('crops').select('*').execute().data
        
        try:
            model = joblib.load('crop_model.joblib')
        except:
            model = train_model(all_crops)
        
        recommendations = []
        
        for item in cart_items:
            item_features = [
                len(item['name']),
                float(item['price']),
                float(item.get('quantity', 1)),
                1 if 'vegetable' in item['type'].lower() else 0,
                1 if 'fruit' in item['type'].lower() else 0,
                1 if 'rice' in item['type'].lower() else 0,
                float(item['price']) / float(item.get('quantity', 1))
            ]
            
            distances, indices = model.kneighbors([item_features])
            
            for idx in indices[0]:
                if all_crops[idx]['id'] != item.get('id'):
                    recommendations.append({
                        **all_crops[idx],
                        'similarity_score': 1 - distances[0][indices[0].tolist().index(idx)]
                    })
        
        # Sort by similarity score and remove duplicates
        unique_recs = []
        seen_ids = set()
        for crop in sorted(recommendations, key=lambda x: x['similarity_score'], reverse=True):
            if crop['id'] not in seen_ids:
                unique_recs.append(crop)
                seen_ids.add(crop['id'])
        
        return unique_recs[:5]
    except Exception as e:
        print(f"AI Recommendation Error: {str(e)}")
        return []

@app.route('/api/crops', methods=['GET'])
def get_crops():
    try:
        search = request.args.get('search', '')
        crop_type = request.args.get('type', '')
        region = request.args.get('region', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 12))
        
        query = supabase.table('crops').select('*')
        
        if search:
            query = query.ilike('name', f'%{search}%')
        if crop_type:
            query = query.eq('type', crop_type)
        if region:
            query = query.eq('region', region)
        
        # Add pagination
        query = query.range((page-1)*per_page, page*per_page-1)
        
        crops = query.execute()
        return jsonify({
            'success': True,
            'data': crops.data,
            'page': page,
            'per_page': per_page,
            'total': len(crops.data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recommendations', methods=['POST'])
def recommendations():
    try:
        cart_items = request.json.get('cart', [])
        recommendations = get_ai_recommendations(cart_items, supabase)
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'message': 'AI recommendations generated based on your cart items'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/orders', methods=['POST'])
def create_order():
    try:
        order_data = request.json
        user_id = order_data.get('user_id')
        items = order_data.get('items', [])
        shipping_info = order_data.get('shipping_info', {})
        payment_method = order_data.get('payment_method', 'cash_on_delivery')
        
        # Validate required fields
        if not all([user_id, items, shipping_info.get('address'), shipping_info.get('phone')]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        # Calculate total and validate items
        total = 0
        for item in items:
            if not all(k in item for k in ['id', 'name', 'price', 'quantity']):
                return jsonify({
                    'success': False,
                    'error': 'Invalid item format'
                }), 400
            total += item['price'] * item['quantity']
        
        # Create order record
        order_id = str(uuid.uuid4())
        order_record = {
            'id': order_id,
            'user_id': user_id,
            'order_date': datetime.now().isoformat(),
            'total_amount': total,
            'status': 'pending',
            'payment_method': payment_method,
            'shipping_address': shipping_info.get('address'),
            'shipping_region': shipping_info.get('region', ''),
            'shipping_phone': shipping_info.get('phone'),
            'shipping_email': shipping_info.get('email', ''),
            'payment_status': 'pending'
        }
        
        # Insert into Supabase
        supabase.table('orders').insert(order_record).execute()
        
        # Create order items and update crop quantities
        for item in items:
            order_item = {
                'order_id': order_id,
                'crop_id': item['id'],
                'quantity': item['quantity'],
                'unit_price': item['price'],
                'total_price': item['price'] * item['quantity']
            }
            supabase.table('order_items').insert(order_item).execute()
            
            # Update crop quantity in inventory
            supabase.table('crops').update({'quantity': item['remaining_quantity']}).eq('id', item['id']).execute()
        
        # Process payment if not cash on delivery
        if payment_method != 'cash_on_delivery':
            payment_result = process_payment(order_id, total, payment_method)
            if not payment_result.get('success'):
                return jsonify({
                    'success': False,
                    'error': payment_result.get('error', 'Payment failed')
                }), 400
            else:
                supabase.table('orders').update({'payment_status': 'completed'}).eq('id', order_id).execute()
        
        # Send confirmation email
        send_order_confirmation(order_record, items)
        
        return jsonify({
            'success': True,
            'order_id': order_id,
            'message': 'Order created successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/orders/<user_id>', methods=['GET'])
def get_user_orders(user_id):
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Get orders with pagination
        orders = supabase.table('orders').select('*').eq('user_id', user_id
            ).order('order_date', desc=True
            ).range((page-1)*per_page, page*per_page-1).execute().data
        
        # Get order items for each order
        for order in orders:
            items = supabase.table('order_items').select('*, crops(name, type, region)').eq('order_id', order['id']).execute().data
            order['items'] = items
        
        # Get total count for pagination
        count = supabase.table('orders').select('count', count='exact').eq('user_id', user_id).execute().count
        
        return jsonify({
            'success': True,
            'data': orders,
            'page': page,
            'per_page': per_page,
            'total': count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/orders/invoice/<order_id>', methods=['GET'])
def generate_invoice(order_id):
    try:
        # Get order data
        order = supabase.table('orders').select('*').eq('id', order_id).execute().data
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        order = order[0]
        items = supabase.table('order_items').select('*, crops(name)').eq('order_id', order_id).execute().data
        
        # Create PDF invoice
        pdf_file = create_invoice_pdf(order, items)
        
        return send_file(
            pdf_file,
            as_attachment=True,
            download_name=f'invoice_{order_id}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def process_payment(order_id, amount, method):
    """Simulate payment processing (in a real app, integrate with bKash API)"""
    if method == 'bkash':
        # In a real implementation, you would:
        # 1. Create payment request to bKash API
        # 2. Verify payment
        # 3. Return success/failure
        return {
            'success': True, 
            'transaction_id': f'BKASH_{uuid.uuid4()}',
            'message': 'bKash payment processed successfully'
        }
    elif method in ['nagad', 'card']:
        return {
            'success': True,
            'transaction_id': f'{method.upper()}_{uuid.uuid4()}',
            'message': f'{method} payment processed successfully'
        }
    else:
        return {
            'success': False, 
            'error': 'Unsupported payment method'
        }

def send_order_confirmation(order, items):
    """Send order confirmation email"""
    if not EMAIL_USER or not EMAIL_PASS:
        print("Email not configured - skipping email sending")
        return
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = order['shipping_email'] or 'customer@example.com'
    msg['Subject'] = f"KrishiGhor Order Confirmation - #{order['id']}"
    
    # Create email body
    email_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #2e7d32; color: white; padding: 15px; text-align: center; }}
            .order-details {{ margin: 20px 0; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
            .total {{ font-weight: bold; font-size: 1.2em; }}
            .footer {{ margin-top: 20px; font-size: 0.9em; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>KrishiGhor - Order Confirmation</h2>
            </div>
            
            <p>Dear Customer,</p>
            <p>Thank you for your order! Your order #{order['id']} has been received and is being processed.</p>
            
            <div class="order-details">
                <h3>Order Summary</h3>
                <table>
                    <tr>
                        <th>Item</th>
                        <th>Quantity</th>
                        <th>Price</th>
                        <th>Total</th>
                    </tr>
    """
    
    for item in items:
        email_body += f"""
                    <tr>
                        <td>{item['crops']['name']}</td>
                        <td>{item['quantity']}</td>
                        <td>৳{item['unit_price']:.2f}</td>
                        <td>৳{item['total_price']:.2f}</td>
                    </tr>
        """
    
    email_body += f"""
                    <tr class="total">
                        <td colspan="3">Total Amount:</td>
                        <td>৳{order['total_amount']:.2f}</td>
                    </tr>
                </table>
            </div>
            
            <div class="shipping-info">
                <h3>Shipping Information</h3>
                <p><strong>Address:</strong> {order['shipping_address']}</p>
                <p><strong>Region:</strong> {order['shipping_region']}</p>
                <p><strong>Phone:</strong> {order['shipping_phone']}</p>
                <p><strong>Email:</strong> {order['shipping_email']}</p>
                <p><strong>Payment Method:</strong> {order['payment_method'].replace('_', ' ').title()}</p>
                <p><strong>Status:</strong> {order['status'].title()}</p>
            </div>
            
            <div class="footer">
                <p>We'll notify you when your order ships. Thank you for shopping with KrishiGhor!</p>
                <p>If you have any questions, please contact our customer support.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(email_body, 'html'))
    
    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

def create_invoice_pdf(order, items):
    """Generate PDF invoice using ReportLab"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    filename = temp_file.name
    
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(name='InvoiceTitle', fontSize=18, alignment=1, spaceAfter=12))
    styles.add(ParagraphStyle(name='InvoiceHeader', fontSize=12, spaceAfter=6))
    styles.add(ParagraphStyle(name='InvoiceText', fontSize=10, spaceAfter=12))
    
    elements = []
    
    # Header
    elements.append(Paragraph("KrishiGhor - Bangladesh Crop Marketplace", styles['InvoiceTitle']))
    elements.append(Paragraph("Invoice", styles['Heading1']))
    elements.append(Spacer(1, 12))
    
    # Order info
    elements.append(Paragraph(f"<b>Order ID:</b> {order['id']}", styles['InvoiceHeader']))
    elements.append(Paragraph(f"<b>Date:</b> {datetime.fromisoformat(order['order_date']).strftime('%B %d, %Y %I:%M %p')}", styles['InvoiceHeader']))
    elements.append(Paragraph(f"<b>Status:</b> {order['status'].capitalize()}", styles['InvoiceHeader']))
    elements.append(Spacer(1, 24))
    
    # Shipping info
    elements.append(Paragraph("<b>Shipping Information:</b>", styles['Heading2']))
    elements.append(Paragraph(f"<b>Name:</b> {order.get('shipping_name', 'Customer')}", styles['InvoiceText']))
    elements.append(Paragraph(f"<b>Email:</b> {order.get('shipping_email', 'N/A')}", styles['InvoiceText']))
    elements.append(Paragraph(f"<b>Phone:</b> {order.get('shipping_phone', 'N/A')}", styles['InvoiceText']))
    elements.append(Paragraph(f"<b>Address:</b> {order.get('shipping_address', 'N/A')}", styles['InvoiceText']))
    elements.append(Paragraph(f"<b>Region:</b> {order.get('shipping_region', 'N/A')}", styles['InvoiceText']))
    elements.append(Spacer(1, 24))
    
    # Items table
    table_data = [
        ['Item', 'Quantity', 'Unit Price', 'Total'],
        *[[
            item['crops']['name'],
            str(item['quantity']),
            f"৳{item['unit_price']:.2f}",
            f"৳{item['total_price']:.2f}"
        ] for item in items],
        ['', '', '<b>Subtotal:</b>', f"<b>৳{order['total_amount']:.2f}</b>"],
        ['', '', '<b>Shipping:</b>', '৳0.00'],
        ['', '', '<b>Total:</b>', f"<b>৳{order['total_amount']:.2f}</b>"]
    ]
    
    items_table = Table(table_data, colWidths=[250, 80, 80, 80])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -4), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (-2, -2), (-1, -1), 'Helvetica-Bold'),
    ]))
    
    elements.append(items_table)
    elements.append(Spacer(1, 36))
    
    # Payment info
    elements.append(Paragraph("<b>Payment Information:</b>", styles['Heading2']))
    elements.append(Paragraph(f"<b>Method:</b> {order['payment_method'].replace('_', ' ').title()}", styles['InvoiceText']))
    elements.append(Paragraph(f"<b>Status:</b> {order.get('payment_status', 'pending').title()}", styles['InvoiceText']))
    elements.append(Spacer(1, 24))
    
    # Footer
    elements.append(Paragraph("Thank you for your business!", styles['InvoiceText']))
    elements.append(Paragraph("KrishiGhor - Transparent Crop Pricing & Supply Chain Platform", styles['Italic']))
    elements.append(Paragraph("Contact: support@krishighor.com | Phone: +880 1XXX-XXXXXX", styles['Italic']))
    
    # Build PDF
    doc.build(elements)
    return filename

if __name__ == '__main__':
    app.run(debug=True)