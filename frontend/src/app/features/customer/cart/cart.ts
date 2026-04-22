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
  pagedItems: CartItem[] = [];
  imageBaseUrl = environment.imageBaseUrl;
  currentPage: number = 1;
  itemsPerPage: number = 3;

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

    this.cartService.cartItems$.subscribe(items => {
      if (this.cartItems.length !== items.length) {
        this.cartItems = items;
        this.updatePagedItems();
      } else {
        this.cartItems = items;
      }
    });
  }

  updatePagedItems() {
    const startIndex = (this.currentPage - 1) * this.itemsPerPage;
    const endIndex = startIndex + this.itemsPerPage;
    this.pagedItems = this.cartItems.slice(startIndex, endIndex);

    // Tự động lùi trang nếu xóa hết item ở trang hiện tại
    if (this.pagedItems.length === 0 && this.currentPage > 1) {
      this.setPage(this.currentPage - 1);
    }
  }

  setPage(page: number) {
    this.currentPage = page;
    this.updatePagedItems();
  }

  get totalPages(): number {
    return Math.ceil(this.cartItems.length / this.itemsPerPage);
  }

  updateQuantity(productId: number, quantity: number) {
    const itemInView = this.pagedItems.find(i => i.product.product_id === productId);
    
    if (itemInView) {
      itemInView.quantity = quantity;
    }

    this.cartService.updateQuantity(productId, quantity);
  }

  removeItem(productId: number) {
    this.cartService.removeFromCart(productId);
  }

  getSubtotal(): number {
    return this.cartService.getTotalPrice();
  }

  getShippingFee(): number {
    return this.cartItems.length > 0 ? 30000 : 0;
  }

  getTotal(): number {
    return this.getSubtotal() + this.getShippingFee();
  }

  trackByFn(index: number, item: any) {
    return item.product.product_id;
  }

  getFullImageUrl(imageUrl: string): string {
    if (!imageUrl) return 'https://via.placeholder.com/100x100?text=No+Image';
    const baseUrl = this.imageBaseUrl.replace(/\/$/, '');
    const path = imageUrl.startsWith('/') ? imageUrl : `/${imageUrl}`;
    return `${baseUrl}${path}`;
  }
}