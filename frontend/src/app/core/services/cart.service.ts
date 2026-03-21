import { Injectable, inject, effect } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { Product } from '../models';
import { AuthService } from './auth.service';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

export interface CartItem {
  product: Product;
  quantity: number;
}

export interface CartResponse {
  cart_id: number;
  user_id: number;
  last_updated: string;
  cart_items: Array<{
    product_id: number;
    quantity: number;
    cart_item_id: number;
    added_at: string;
    product: Product;
  }>;
}

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
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/cart`;

  constructor() {
    this.loadCart();
    // Clear cart on logout
    effect(() => {
      if (!this.authService.isLoggedIn()) {
        this.clearCart();
      } else {
        // Load cart from backend when logged in
        this.loadCartFromBackend();
      }
    });
  }

  private loadCart() {
    const savedCart = localStorage.getItem('cart');
    if (savedCart) {
      this.cartItems.next(JSON.parse(savedCart));
    }
  }

  cartCount$ = this.cartItems$.pipe(
    map((items: CartItem[]) => this.authService.isLoggedIn() ? items.reduce((acc: number, item: CartItem) => acc + item.quantity, 0) : 0)
  );

  private loadCartFromBackend() {
    const token = sessionStorage.getItem('token');
    if (!token) return;

    const headers = { 'Authorization': `Bearer ${token}` };
    this.http.get<CartResponse>(this.apiUrl, { headers }).subscribe({
      next: (cartData) => {
        // Convert backend cart items to frontend format
        const items: CartItem[] = cartData.cart_items.map(cartItem => ({
          product: cartItem.product,
          quantity: cartItem.quantity
        }));
        this.cartItems.next(items);
        this.saveCart(); // Save to localStorage for offline access
      },
      error: (error) => {
        console.error('Error loading cart from backend:', error);
      }
    });
  }

  addToCart(product: Product, quantity: number = 1) {
    if (!this.authService.isLoggedIn()) {
      // Redirect to login if not authenticated
      this.router.navigate(['/auth/login']);
      return;
    }

    const token = sessionStorage.getItem('token');
    if (!token) {
      this.router.navigate(['/auth/login']);
      return;
    }

    const headers = { 'Authorization': `Bearer ${token}` };
    const cartItem = {
      product_id: product.product_id,
      quantity: quantity
    };

    this.http.post(`${this.apiUrl}/items`, cartItem, { headers }).subscribe({
      next: (response) => {
        // Reload cart from backend after successful add
        this.loadCartFromBackend();
      },
      error: (error) => {
        console.error('Error adding item to cart:', error);
        alert('Failed to add item to cart');
      }
    });
  }

  updateQuantity(productId: number, quantity: number) {
    if (!this.authService.isLoggedIn()) return;

    const token = sessionStorage.getItem('token');
    if (!token) return;

    // Find cart item ID from current items
    const currentItems = this.cartItems.value;
    const item = currentItems.find(item => item.product.product_id === productId);
    if (!item) return;

    // For now, we'll reload from backend after update
    // In a real app, you'd track cart_item_id
    const headers = { 'Authorization': `Bearer ${token}` };
    const cartItem = {
      product_id: productId,
      quantity: quantity
    };

    if (quantity <= 0) {
      // Remove item
      this.http.delete(`${this.apiUrl}/items/${item.product.product_id}`, { headers }).subscribe({
        next: () => this.loadCartFromBackend(),
        error: (error) => console.error('Error removing item:', error)
      });
    } else {
      // Update quantity - for simplicity, we'll remove and re-add
      // In production, you'd use PUT /cart/items/{cart_item_id}
      this.http.delete(`${this.apiUrl}/items/${item.product.product_id}`, { headers }).subscribe({
        next: () => {
          this.http.post(`${this.apiUrl}/items`, cartItem, { headers }).subscribe({
            next: () => this.loadCartFromBackend(),
            error: (error) => console.error('Error updating item:', error)
          });
        },
        error: (error) => console.error('Error removing item for update:', error)
      });
    }
  }

  removeFromCart(productId: number) {
    if (!this.authService.isLoggedIn()) return;

    const token = sessionStorage.getItem('token');
    if (!token) return;

    const headers = { 'Authorization': `Bearer ${token}` };
    this.http.delete(`${this.apiUrl}/items/${productId}`, { headers }).subscribe({
      next: () => this.loadCartFromBackend(),
      error: (error) => console.error('Error removing item:', error)
    });
  }

  clearCart() {
    this.cartItems.next([]);
    localStorage.removeItem('cart');
  }

  getTotalPrice(): number {
    return this.cartItems.value.reduce((total, item) => total + (Number(item.product.price) * item.quantity), 0);
  }

  getItemCount(): number {
    return this.cartItems.value.reduce((total, item) => total + item.quantity, 0);
  }
}
