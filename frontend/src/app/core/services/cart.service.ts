import { Injectable, inject, effect } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { Product } from '../models';
import { AuthService } from './auth.service';
import { Router } from '@angular/router';

export interface CartItem {
  product: Product;
  quantity: number;
}

@Injectable({
  providedIn: 'root'
})
export class CartService {
  private cartItems = new BehaviorSubject<CartItem[]>([]);
  cartItems$ = this.cartItems.asObservable();
  private authService = inject(AuthService);
  private router = inject(Router);

  constructor() {
    this.loadCart();
    // Clear cart on logout
    effect(() => {
      if (!this.authService.isLoggedIn()) {
        this.clearCart();
      }
    });
  }

  private loadCart() {
    const savedCart = localStorage.getItem('cart');
    if (savedCart) {
      this.cartItems.next(JSON.parse(savedCart));
    }
  }

  private saveCart() {
    localStorage.setItem('cart', JSON.stringify(this.cartItems.value));
  }

  addToCart(product: Product, quantity: number = 1) {
    if (!this.authService.isLoggedIn()) {
      // Redirect to login if not authenticated
      this.router.navigate(['/auth/login']);
      return;
    }
    const currentItems = this.cartItems.value;
    const existingItem = currentItems.find(item => item.product.product_id === product.product_id);

    if (existingItem) {
      existingItem.quantity += quantity;
      this.cartItems.next([...currentItems]);
    } else {
      this.cartItems.next([...currentItems, { product, quantity }]);
    }
    this.saveCart();
  }

  updateQuantity(productId: number, quantity: number) {
    const currentItems = this.cartItems.value;
    const existingItem = currentItems.find(item => item.product.product_id === productId);

    if (existingItem) {
      if (quantity <= 0) {
        this.removeFromCart(productId);
      } else {
        existingItem.quantity = quantity;
        this.cartItems.next([...currentItems]);
        this.saveCart();
      }
    }
  }

  removeFromCart(productId: number) {
    const currentItems = this.cartItems.value;
    this.cartItems.next(currentItems.filter(item => item.product.product_id !== productId));
    this.saveCart();
  }

  clearCart() {
    this.cartItems.next([]);
    this.saveCart();
  }

  getTotalPrice(): number {
    return this.cartItems.value.reduce((total, item) => total + (Number(item.product.price) * item.quantity), 0);
  }

  getItemCount(): number {
    return this.cartItems.value.reduce((total, item) => total + item.quantity, 0);
  }
}
