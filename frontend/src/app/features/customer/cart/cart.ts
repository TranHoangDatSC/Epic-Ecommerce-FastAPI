import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { CartService, CartItem } from '../../../core/services/cart.service';
import { AuthService } from '../../../core/services/auth.service';
import { environment } from '../../../../environments/environment';

@Component({
  selector: 'app-cart',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './cart.html',
  styleUrls: ['./cart.scss']
})
export class CartComponent implements OnInit {
  cartItems: CartItem[] = [];
  groupedItems: { method: number; items: CartItem[] }[] = [];
  imageBaseUrl = environment.imageBaseUrl;

  constructor(
    private cartService: CartService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    if (!this.authService.isLoggedIn()) {
      this.router.navigate(['/auth/login']);
      return;
    }

    // Cart service will automatically load from backend when logged in
    this.cartService.cartItems$.subscribe(items => {
      this.cartItems = items;
      this.groupItems();
    });
  }

  groupItems() {
    const groups: Map<number, CartItem[]> = new Map();
    this.cartItems.forEach(item => {
      const method = item.product.transfer_method || 1;
      if (!groups.has(method)) {
        groups.set(method, []);
      }
      groups.get(method)!.push(item);
    });

    this.groupedItems = Array.from(groups.entries()).map(([method, items]) => ({
      method,
      items
    }));
  }

  getTransferMethodLabel(method: number): string {
    return method === 2 ? 'Nhận tại cửa hàng / Giao dịch trực tiếp' : 'Giao hàng tận nơi (Ship)';
  }

  getTransferMethodIcon(method: number): string {
    return method === 2 ? 'bi-person-walking' : 'bi-truck';
  }

  getTransferMethodClass(method: number): string {
    return method === 2 ? 'method-pickup' : 'method-shipping';
  }

  updateQuantity(productId: number, quantity: number) {
    this.cartService.updateQuantity(productId, quantity);
  }

  removeItem(productId: number) {
    this.cartService.removeFromCart(productId);
  }

  getSubtotal(): number {
    return this.cartService.getTotalPrice();
  }

  getShippingFee(): number {
    // Basic logic: free for pickup, flat fee for shipping
    const hasShipping = this.cartItems.some(item => (item.product.transfer_method || 1) === 1);
    return hasShipping ? 30000 : 0;
  }

  getTotal(): number {
    return this.getSubtotal() + this.getShippingFee();
  }

  getFullImageUrl(imageUrl: string): string {
    if (!imageUrl) return 'https://via.placeholder.com/100x100?text=No+Image';
    const baseUrl = this.imageBaseUrl.replace(/\/$/, '');
    const path = imageUrl.startsWith('/') ? imageUrl : `/${imageUrl}`;
    return `${baseUrl}${path}`;
  }
}
