-- Create tables
CREATE TABLE IF NOT EXISTS crops (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    quantity DECIMAL(10, 2) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    region VARCHAR(100) NOT NULL,
    description TEXT,
    image_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('farmer', 'buyer', 'trader', 'admin')),
    full_name VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    region VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    order_date TIMESTAMP NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled')),
    payment_method VARCHAR(20) NOT NULL CHECK (payment_method IN ('cash_on_delivery', 'bkash', 'nagad', 'card')),
    payment_status VARCHAR(20) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'completed', 'failed', 'refunded')),
    shipping_name VARCHAR(100),
    shipping_address TEXT NOT NULL,
    shipping_region VARCHAR(100) NOT NULL,
    shipping_phone VARCHAR(20) NOT NULL,
    shipping_email VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    crop_id INTEGER NOT NULL REFERENCES crops(id),
    quantity DECIMAL(10, 2) NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY,
    order_id UUID NOT NULL REFERENCES orders(id),
    amount DECIMAL(12, 2) NOT NULL,
    method VARCHAR(20) NOT NULL,
    transaction_id VARCHAR(100),
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    payment_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_crop_region ON crops(region);
CREATE INDEX idx_crop_type ON crops(type);
CREATE INDEX idx_crop_price ON crops(price);
CREATE INDEX idx_user_type ON users(user_type);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_crop_id ON order_items(crop_id);
CREATE INDEX idx_payments_order_id ON payments(order_id);

-- Insert sample data
INSERT INTO users (username, email, password_hash, user_type, full_name, phone, address, region) VALUES
('admin', 'admin@krishighor.com', '$2a$10$xJwL5v5Jz5UZJZ5UZJZ5Ue5UZJZ5UZJZ5UZJZ5UZJZ5UZJZ5UZJZ5U', 'admin', 'Admin User', '+8801712345678', 'Farmgate, Dhaka', 'Dhaka'),
('farmer1', 'farmer1@example.com', '$2a$10$xJwL5v5Jz5UZJZ5UZJZ5Ue5UZJZ5UZJZ5UZJZ5UZJZ5UZJZ5UZJZ5U', 'farmer', 'Abdul Rahman', '+8801711111111', 'Bogra', 'Bogra'),
('buyer1', 'buyer1@example.com', '$2a$10$xJwL5v5Jz5UZJZ5UZJZ5Ue5UZJZ5UZJZ5UZJZ5UZJZ5UZJZ5UZJZ5U', 'buyer', 'Kamal Hossain', '+8801722222222', 'Mirpur, Dhaka', 'Dhaka'),
('trader1', 'trader1@example.com', '$2a$10$xJwL5v5Jz5UZJZ5UZJZ5Ue5UZJZ5UZJZ5UZJZ5UZJZ5UZJZ5UZJZ5U', 'trader', 'Rahim Traders', '+8801733333333', 'Chittagong', 'Chittagong');

INSERT INTO crops (name, type, quantity, price, region, description) VALUES
('BRRI Dhan 89', 'Rice', 10000.00, 38.00, 'Barisal', 'High-yielding Aman variety with good grain quality'),
('BARI Mung-8', 'Pulse', 5000.00, 120.00, 'Khulna', 'Drought-resistant mung bean variety with high protein content'),
('BARI Tomato-14', 'Vegetable', 8000.00, 25.00, 'Rangpur', 'Hybrid tomato variety with disease resistance'),
('BINA Chinabadam-8', 'Nut', 3000.00, 300.00, 'Dinajpur', 'High-yielding peanut variety with good oil content'),
('Fazli Mango', 'Fruit', 6000.00, 80.00, 'Rajshahi', 'Premium seasonal mango with excellent flavor'),
('White Jute (Tossa)', 'Fiber', 7000.00, 50.00, 'Faridpur', 'Grade-1 jute fiber for high quality products'),
('BARI Alu-8', 'Vegetable', 12000.00, 20.00, 'Bogra', 'High-starch potato variety good for chips and processing'),
('BARI Sarisha-17', 'Oilseed', 4000.00, 65.00, 'Jessore', 'Canola-type mustard with high oil yield'),
('BARI Piaz-4', 'Vegetable', 9000.00, 35.00, 'Pabna', 'Long-storage onion variety with good pungency'),
('BRRI Dhan 28', 'Rice', 15000.00, 32.00, 'Comilla', 'Popular Boro rice variety with high yield potential'),
('BARI Misti Kodu-1', 'Vegetable', 3000.00, 40.00, 'Sylhet', 'Sweet pumpkin variety with high beta-carotene'),
('BARI Strawberry-1', 'Fruit', 1000.00, 200.00, 'Rangpur', 'First ever strawberry variety developed for Bangladesh');