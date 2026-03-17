export enum Role {
  ADMIN = 'ADMIN',
  MOD = 'MOD',
  SELLER = 'SELLER',
  CUSTOMER = 'CUSTOMER'
}

export interface User {
  id: number;
  username: string;
  email: string;
  role: Role;
  createdAt: Date;
  updatedAt: Date;
}

export interface ProductImage {
  image_id: number;
  image_url: string;
  alt_text?: string;
  is_primary: boolean;
  display_order: number;
}

export interface Product {
  product_id: number;
  title: string;
  description?: string;
  price: number;
  quantity: number;
  category_id: number;
  seller_id: number;
  status: number;
  reject_reason?: string;
  view_count: number;
  is_deleted: boolean;
  created_at: string;
  updated_at?: string;
  is_approved: boolean;
  product_images: ProductImage[];
  seller?: User;
}

export interface Order {
  id: number;
  userId: number;
  totalAmount: number;
  status: string;
  createdAt: Date;
  updatedAt: Date;
  orderDetails: OrderDetail[];
}

export interface OrderDetail {
  id: number;
  orderId: number;
  productId: number;
  quantity: number;
  price: number;
}

export interface Category {
  id: number;
  name: string;
  description: string;
}