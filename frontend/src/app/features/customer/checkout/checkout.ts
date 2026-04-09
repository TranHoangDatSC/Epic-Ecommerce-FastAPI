import { Component, OnInit, inject , ChangeDetectorRef} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { CartService, CartItem } from '../../../core/services/cart.service';
import { ContactService, ContactInfo } from '../../../shared/services/contact.service';
import { OrderService, PaymentMethod, OrderCreate } from '../../../shared/services/order.service';
import { UIService } from '../../../core/services/ui.service';

import { environment } from '../../../../environments/environment';

@Component({
  selector: 'app-checkout',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './checkout.html',
  styleUrls: ['./checkout.scss']
})
export class CheckoutComponent implements OnInit {
  private cartService = inject(CartService);
  private contactService = inject(ContactService);
  private orderService = inject(OrderService);
  private uiService = inject(UIService);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);

  cartItems: CartItem[] = [];
  addresses: ContactInfo[] = [];
  paymentMethods: PaymentMethod[] = [];
  imageBaseUrl = environment.imageBaseUrl;
  
  selectedAddressId: number | null = null;
  selectedPaymentMethodId: number | null = null;
  orderNotes: string = '';
  
  isLoading = true;
  isSubmitting = false;
  
  shippingFee = 30000; // Fixed shipping fee for demonstration

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.isLoading = true;
    
    // Load cart items
    this.cartService.cartItems$.subscribe(items => {
      this.cartItems = items;
      if (items.length === 0 && !this.isLoading) {
        this.router.navigate(['/cart']);
      }
    });

    // Load addresses
    this.contactService.getContactInfos().subscribe({
      next: (data) => {
        this.addresses = data;
        const defaultAddr = data.find(a => a.is_default);
        if (defaultAddr) {
          this.selectedAddressId = defaultAddr.contact_id || null;
        } else if (data.length > 0) {
          this.selectedAddressId = data[0].contact_id || null;
        }
      },
      error: (err) => console.error('Error loading addresses:', err)
    });

    // Load payment methods
    this.orderService.getPaymentMethods().subscribe({
      next: (data) => {
        this.paymentMethods = data;
        if (data.length > 0) {
          this.selectedPaymentMethodId = data[0].payment_method_id;
        }
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error loading payment methods:', err);
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  getSubtotal(): number {
    return this.cartService.getTotalPrice();
  }

  getTotal(): number {
    return this.getSubtotal() + this.shippingFee;
  }

  selectAddress(id: number | undefined): void {
    if (id) {
      this.selectedAddressId = id;
      this.cdr.detectChanges();
    }
  }

  selectPaymentMethod(id: number): void {
    this.selectedPaymentMethodId = id;
    this.cdr.detectChanges();
  }

  placeOrder(): void {
    if (!this.selectedAddressId || !this.selectedPaymentMethodId) {
      this.uiService.showError('Vui lòng chọn địa chỉ giao hàng và phương thức thanh toán!');
      return;
    }

    if (this.cartItems.length === 0) {
      this.uiService.showError('Giỏ hàng của bạn đang trống!');
      return;
    }

    this.isSubmitting = true;
    
    const orderData: OrderCreate = {
      contact_id: this.selectedAddressId,
      payment_method_id: this.selectedPaymentMethodId,
      order_items: this.cartItems.map(item => ({
        product_id: item.product.product_id,
        quantity: item.quantity
      })),
      shipping_fee: this.shippingFee,
      notes: this.orderNotes
    };

    this.orderService.createOrder(orderData).subscribe({
      next: (res) => {
        this.uiService.showSuccess('Đặt hàng thành công!');
        this.cartService.clearCart();
        this.router.navigate(['/customer/profile/orders']);
        this.isSubmitting = false;
      },
      error: (err) => {
        console.error('Order Error:', err);
        const errorMsg = err.error?.detail || 'Đã có lỗi xảy ra khi đặt hàng. Vui lòng thử lại!';
        this.uiService.showError(errorMsg);
        this.isSubmitting = false;
      }
    });
  }

  getFullImageUrl(imageUrl: string): string {
    if (!imageUrl) return 'https://via.placeholder.com/100x100?text=No+Image';
    const baseUrl = this.imageBaseUrl.replace(/\/$/, '');
    const path = imageUrl.startsWith('/') ? imageUrl : `/${imageUrl}`;
    return `${baseUrl}${path}`;
  }
}
