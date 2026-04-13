export enum Role {
  ADMIN = 'ADMIN',
  MOD = 'MOD',
  SELLER = 'SELLER',
  CUSTOMER = 'CUSTOMER'
}

export interface User {
  user_id: number;
  username: string;
  email: string;
  full_name: string;
  phone_number?: string;
  address?: string;
  avatar_url?: string;
  role?: Role;
  trust_score?: number;
  created_at: string;
  updated_at?: string;
}

export interface ProductImage {
  image_id: number;
  image_url: string;
  alt_text?: string;
  is_primary: boolean;
  display_order: number;
}

export interface Review {
  review_id: number;
  product_id: number;
  buyer_id: number;
  rating: number;
  content: string;
  created_at: string;
  reviewer?: User;
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
  transfer_method: number;
  is_approved: boolean;
  product_images: ProductImage[];
  seller?: User;
  reviews: Review[];
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
  category_id: number;
  name: string;
  description: string;
  // Optional alias for convenience in templates
  id?: number;
}