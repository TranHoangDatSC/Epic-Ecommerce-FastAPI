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

export interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  categoryId: number;
  sellerId: number;
  images: string[];
  createdAt: Date;
  updatedAt: Date;
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