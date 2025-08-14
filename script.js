// Add these new functions to your existing script.js

// User authentication state (simplified for demo)
let currentUser = {
    id: 1,
    username: 'demo_user',
    email: 'user@example.com',
    user_type: 'buyer'
};

// Enhanced checkout function
async function handleCheckout() {
    if (cart.length === 0) {
        showToast('Your cart is empty!', 'error');
        return;
    }

    // Show checkout modal
    const checkoutModal = document.createElement('div');
    checkoutModal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4';
    checkoutModal.innerHTML = `
        <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div class="p-6">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-xl font-bold">Checkout</h3>
                    <button id="close-checkout" class="text-gray-500 hover:text-gray-700">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <h4 class="font-bold mb-2">Shipping Information</h4>
                        <div class="space-y-3">
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                                <input type="text" id="shipping-name" class="w-full px-3 py-2 border rounded-md" value="Demo User">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                                <input type="email" id="shipping-email" class="w-full px-3 py-2 border rounded-md" value="${currentUser.email}">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
                                <input type="tel" id="shipping-phone" class="w-full px-3 py-2 border rounded-md" value="+8801XXXXXXXXX">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Region</label>
                                <select id="shipping-region" class="w-full px-3 py-2 border rounded-md">
                                    <option>Dhaka</option>
                                    <option>Chittagong</option>
                                    <option>Khulna</option>
                                    <option>Rajshahi</option>
                                    <option>Sylhet</option>
                                    <option>Barisal</option>
                                    <option>Rangpur</option>
                                    <option>Mymensingh</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Address</label>
                                <textarea id="shipping-address" class="w-full px-3 py-2 border rounded-md" rows="3">123 Farmgate, Dhaka</textarea>
                            </div>
                        </div>
                    </div>
                    
                    <div>
                        <h4 class="font-bold mb-2">Order Summary</h4>
                        <div class="bg-gray-50 p-4 rounded-lg">
                            <div id="checkout-items" class="space-y-2 mb-4">
                                ${cart.map(item => `
                                    <div class="flex justify-between">
                                        <span>${item.name} x${item.quantity}</span>
                                        <span>৳${(item.price * item.quantity).toFixed(2)}</span>
                                    </div>
                                `).join('')}
                            </div>
                            <div class="border-t pt-2">
                                <div class="flex justify-between font-bold">
                                    <span>Total:</span>
                                    <span id="checkout-total">৳${cart.reduce((sum, item) => sum + (item.quantity * item.price), 0).toFixed(2)}</span>
                                </div>
                            </div>
                            
                            <div class="mt-6">
                                <h4 class="font-bold mb-2">Payment Method</h4>
                                <div class="space-y-2">
                                    <label class="flex items-center space-x-2">
                                        <input type="radio" name="payment-method" value="cash_on_delivery" checked class="rounded-full">
                                        <span>Cash on Delivery</span>
                                    </label>
                                    <label class="flex items-center space-x-2">
                                        <input type="radio" name="payment-method" value="bkash" class="rounded-full">
                                        <span>bKash</span>
                                    </label>
                                    <div id="bkash-details" class="hidden pl-6 mt-2 space-y-2">
                                        <div>
                                            <label class="block text-sm font-medium text-gray-700 mb-1">bKash Number</label>
                                            <input type="tel" id="bkash-number" class="w-full px-3 py-2 border rounded-md" placeholder="01XXXXXXXXX">
                                        </div>
                                        <div>
                                            <label class="block text-sm font-medium text-gray-700 mb-1">Transaction ID</label>
                                            <input type="text" id="bkash-trx" class="w-full px-3 py-2 border rounded-md" placeholder="TRX123456789">
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <button id="place-order-btn" class="w-full mt-6 bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg">
                                Place Order
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(checkoutModal);
    
    // Setup event listeners for the modal
    document.getElementById('close-checkout').addEventListener('click', () => {
        checkoutModal.remove();
    });
    
    // Show/hide bKash details based on payment method selection
    document.querySelectorAll('input[name="payment-method"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            const bkashDetails = document.getElementById('bkash-details');
            bkashDetails.classList.toggle('hidden', e.target.value !== 'bkash');
        });
    });
    
    // Handle place order button
    document.getElementById('place-order-btn').addEventListener('click', async () => {
        const shippingInfo = {
            name: document.getElementById('shipping-name').value,
            email: document.getElementById('shipping-email').value,
            phone: document.getElementById('shipping-phone').value,
            region: document.getElementById('shipping-region').value,
            address: document.getElementById('shipping-address').value
        };
        
        const paymentMethod = document.querySelector('input[name="payment-method"]:checked').value;
        let paymentDetails = {};
        
        if (paymentMethod === 'bkash') {
            paymentDetails = {
                bkash_number: document.getElementById('bkash-number').value,
                transaction_id: document.getElementById('bkash-trx').value
            };
            
            if (!paymentDetails.bkash_number || !paymentDetails.transaction_id) {
                showToast('Please provide bKash payment details', 'error');
                return;
            }
        }
        
        try {
            const response = await fetch(`${API_BASE}/orders`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: currentUser.id,
                    items: cart,
                    shipping_info: shippingInfo,
                    payment_method: paymentMethod
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                showToast('Order placed successfully!', 'success');
                cart = [];
                updateCartUI();
                getAiRecommendations();
                checkoutModal.remove();
                toggleCart();
                
                // Show order confirmation
                showOrderConfirmation(data.order_id);
            } else {
                showToast(data.error || 'Failed to place order', 'error');
            }
        } catch (error) {
            console.error('Order error:', error);
            showToast('Failed to place order', 'error');
        }
    });
}

function showOrderConfirmation(orderId) {
    const confirmationModal = document.createElement('div');
    confirmationModal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4';
    confirmationModal.innerHTML = `
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div class="p-6">
                <div class="text-center mb-4">
                    <i class="fas fa-check-circle text-5xl text-green-500 mb-3"></i>
                    <h3 class="text-xl font-bold">Order Confirmed!</h3>
                    <p class="text-gray-600 mt-1">Your order #${orderId} has been placed successfully.</p>
                </div>
                
                <div class="bg-gray-50 p-4 rounded-lg mb-4">
                    <p class="text-center mb-2">You can track your order in your dashboard.</p>
                    <div class="flex justify-center space-x-3">
                        <button id="view-invoice" class="px-4 py-2 bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200">
                            <i class="fas fa-file-invoice mr-2"></i> View Invoice
                        </button>
                        <button id="go-to-dashboard" class="px-4 py-2 bg-green-100 text-green-700 rounded-md hover:bg-green-200">
                            <i class="fas fa-tachometer-alt mr-2"></i> Dashboard
                        </button>
                    </div>
                </div>
                
                <button id="close-confirmation" class="w-full mt-4 py-2 bg-gray-100 rounded-md hover:bg-gray-200">
                    Continue Shopping
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(confirmationModal);
    
    // Setup event listeners
    document.getElementById('close-confirmation').addEventListener('click', () => {
        confirmationModal.remove();
    });
    
    document.getElementById('go-to-dashboard').addEventListener('click', () => {
        confirmationModal.remove();
        showBuyerDashboard();
    });
    
    document.getElementById('view-invoice').addEventListener('click', async () => {
        try {
            const response = await fetch(`${API_BASE}/orders/invoice/${orderId}`);
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `invoice_${orderId}.pdf`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            } else {
                const error = await response.json();
                showToast(error.error || 'Failed to download invoice', 'error');
            }
        } catch (error) {
            console.error('Invoice download error:', error);
            showToast('Failed to download invoice', 'error');
        }
    });
}

function showBuyerDashboard() {
    // In a real app, you would have a proper router/navigation system
    // For this demo, we'll just show a simplified dashboard
    
    // Hide main content
    document.querySelector('main').classList.add('hidden');
    document.getElementById('ai-section').classList.add('hidden');
    
    // Create dashboard container
    const dashboard = document.createElement('div');
    dashboard.className = 'container mx-auto px-4 py-8';
    dashboard.id = 'buyer-dashboard';
    dashboard.innerHTML = `
        <div class="flex justify-between items-center mb-6">
            <h2 class="text-2xl font-bold">My Dashboard</h2>
            <button id="back-to-shop" class="px-4 py-2 bg-gray-100 rounded-md hover:bg-gray-200">
                <i class="fas fa-arrow-left mr-2"></i> Back to Shop
            </button>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="bg-white p-6 rounded-lg shadow border border-gray-100">
                <h3 class="font-bold text-lg mb-2">Recent Orders</h3>
                <p class="text-3xl font-bold text-green-600" id="order-count">0</p>
                <p class="text-sm text-gray-500">orders placed</p>
            </div>
            <div class="bg-white p-6 rounded-lg shadow border border-gray-100">
                <h3 class="font-bold text-lg mb-2">Pending Orders</h3>
                <p class="text-3xl font-bold text-yellow-600" id="pending-count">0</p>
                <p class="text-sm text-gray-500">awaiting delivery</p>
            </div>
            <div class="bg-white p-6 rounded-lg shadow border border-gray-100">
                <h3 class="font-bold text-lg mb-2">Total Spent</h3>
                <p class="text-3xl font-bold text-blue-600" id="total-spent">৳0</p>
                <p class="text-sm text-gray-500">all time</p>
            </div>
        </div>
        
        <div class="bg-white p-6 rounded-lg shadow mb-8">
            <div class="flex justify-between items-center mb-4">
                <h3 class="font-bold text-lg">Order History</h3>
                <button id="refresh-orders" class="text-green-600 hover:text-green-800">
                    <i class="fas fa-sync-alt mr-1"></i> Refresh
                </button>
            </div>
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order ID</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Items</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="orders-table-body" class="bg-white divide-y divide-gray-200">
                        <tr>
                            <td colspan="6" class="px-6 py-4 text-center text-gray-500">Loading orders...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    `;
    
    // Insert dashboard before footer
    document.querySelector('main').insertAdjacentElement('beforebegin', dashboard);
    
    // Load orders
    loadUserOrders();
    
    // Setup event listeners
    document.getElementById('back-to-shop').addEventListener('click', () => {
        dashboard.remove();
        document.querySelector('main').classList.remove('hidden');
        document.getElementById('ai-section').classList.remove('hidden');
    });
    
    document.getElementById('refresh-orders').addEventListener('click', loadUserOrders);
}

async function loadUserOrders() {
    try {
        const response = await fetch(`${API_BASE}/orders/${currentUser.id}`);
        const data = await response.json();
        
        if (data.success) {
            const orders = data.orders;
            
            // Update summary cards
            document.getElementById('order-count').textContent = orders.length;
            document.getElementById('pending-count').textContent = 
                orders.filter(o => o.status === 'pending' || o.status === 'processing').length;
            document.getElementById('total-spent').textContent = 
                '৳' + orders.reduce((sum, order) => sum + order.total_amount, 0).toFixed(2);
            
            // Update orders table
            const ordersTable = document.getElementById('orders-table-body');
            if (orders.length === 0) {
                ordersTable.innerHTML = `
                    <tr>
                        <td colspan="6" class="px-6 py-4 text-center text-gray-500">No orders found</td>
                    </tr>
                `;
                return;
            }
            
            ordersTable.innerHTML = orders.map(order => `
                <tr>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        #${order.id.slice(0, 8)}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        ${new Date(order.order_date).toLocaleDateString()}
                    </td>
                    <td class="px-6 py-4 text-sm text-gray-500">
                        ${order.items.length} item${order.items.length !== 1 ? 's' : ''}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        ৳${order.total_amount.toFixed(2)}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="px-2 py-1 text-xs rounded-full 
                            ${order.status === 'delivered' ? 'bg-green-100 text-green-800' : 
                              order.status === 'cancelled' ? 'bg-red-100 text-red-800' : 
                              'bg-yellow-100 text-yellow-800'}">
                            ${order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button class="view-order text-green-600 hover:text-green-900 mr-3" data-id="${order.id}">
                            <i class="fas fa-eye mr-1"></i> View
                        </button>
                        <button class="download-invoice text-blue-600 hover:text-blue-900" data-id="${order.id}">
                            <i class="fas fa-download mr-1"></i> Invoice
                        </button>
                    </td>
                </tr>
            `).join('');
            
            // Add event listeners to view order buttons
            document.querySelectorAll('.view-order').forEach(btn => {
                btn.addEventListener('click', () => viewOrderDetails(btn.dataset.id));
            });
            
            // Add event listeners to download invoice buttons
            document.querySelectorAll('.download-invoice').forEach(btn => {
                btn.addEventListener('click', () => downloadInvoice(btn.dataset.id));
            });
            
        } else {
            showToast(data.error || 'Failed to load orders', 'error');
        }
    } catch (error) {
        console.error('Error loading orders:', error);
        showToast('Failed to load orders', 'error');
    }
}

function viewOrderDetails(orderId) {
    // In a real app, you would fetch the full order details
    // For this demo, we'll just show a simple modal
    showToast(`Viewing order #${orderId}`, 'info');
}

async function downloadInvoice(orderId) {
    try {
        const response = await fetch(`${API_BASE}/orders/invoice/${orderId}`);
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `invoice_${orderId}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } else {
            const error = await response.json();
            showToast(error.error || 'Failed to download invoice', 'error');
        }
    } catch (error) {
        console.error('Invoice download error:', error);
        showToast('Failed to download invoice', 'error');
    }
}

// Add dashboard button to header (after the cart button)
const headerActions = document.querySelector('header div.flex.items-center.space-x-4');
const dashboardBtn = document.createElement('button');
dashboardBtn.id = 'dashboard-btn';
dashboardBtn.className = 'p-2 rounded-full bg-green-800 hover:bg-green-900 text-white';
dashboardBtn.innerHTML = '<i class="fas fa-tachometer-alt"></i>';
dashboardBtn.title = 'Dashboard';
dashboardBtn.addEventListener('click', showBuyerDashboard);

headerActions.insertBefore(dashboardBtn, document.getElementById('cart-btn'));