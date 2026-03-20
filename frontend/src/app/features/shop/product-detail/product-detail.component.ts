import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, ActivatedRoute } from '@angular/router';
import { Product, ProductImage } from '../../../core/models';
import { environment } from '../../../../environments/environment';
import { ProductService } from '../../../shared/services/product.service';
import { CartService } from '../../../core/services/cart.service';

declare var bootstrap: any;

@Component({
  selector: 'app-product-detail',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './product-detail.component.html',
  styleUrls: ['./product-detail.component.scss']
})
export class ProductDetailComponent implements OnInit {
  product: Product | null = null;
  primaryImage: ProductImage | null = null;
  secondaryImages: ProductImage[] = [];
  imageBaseUrl = environment.imageBaseUrl;

  constructor(
    private route: ActivatedRoute,
    private productService: ProductService,
    private cartService: CartService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      const id = +params['id'];
      if (id) {
        this.loadProduct(id);
      }
    });
  }

  private loadProduct(id: number): void {
    this.productService.getProduct(id).subscribe({
      next: (product) => {
        this.product = product;
        this.setImages();
        this.cdr.detectChanges();
      },
      error: (error) => {
        console.error('Error loading product details:', error);
        this.cdr.detectChanges();
      }
    });
  }

  private setImages(): void {
    if (this.product?.product_images) {
      this.primaryImage = this.product.product_images.find(img => img.is_primary) || null;
      this.secondaryImages = this.product.product_images.filter(img => !img.is_primary);
    }
  }

  getFullImageUrl(imageUrl: string): string {
    if (!imageUrl) return 'https://via.placeholder.com/600x600?text=No+Image';
    const baseUrl = this.imageBaseUrl.replace(/\/$/, '');
    const path = imageUrl.startsWith('/') ? imageUrl : `/${imageUrl}`;
    return `${baseUrl}${path}`;
  }

  setPrimaryImage(image: ProductImage): void {
    this.primaryImage = image;
  }

  reportingType: 'product' | 'review' | null = null;
  reportingId: number | null = null;
  reportCategory: string = '';
  reportReason: string = '';
  couponCode: string = '';

  applyCoupon(): void {
    if (!this.couponCode.trim()) {
      alert('Vui lòng nhập mã giảm giá!');
      return;
    }
    alert(`Đang kiểm tra mã: ${this.couponCode}. Tính năng này sẽ sớm ra mắt!`);
  }

  reportProduct(): void {
    this.reportingType = 'product';
    this.reportingId = this.product?.product_id || null;
    this.reportCategory = '';
    this.reportReason = '';
    const modalElement = document.getElementById('reportModal');
    if (modalElement) {
      const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
      modal.show();
    }
  }

  reportReview(reviewId: number): void {
    this.reportingType = 'review';
    this.reportingId = reviewId;
    this.reportCategory = '';
    this.reportReason = '';
    const modalElement = document.getElementById('reportModal');
    if (modalElement) {
      const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
      modal.show();
    }
  }

  submitReport(): void {
    if (!this.reportCategory) {
      alert('Vui lòng chọn lý do báo cáo!');
      return;
    }

    const typeLabel = this.reportingType === 'product' ? 'Sản phẩm' : 'Đánh giá';
    console.log(`Báo cáo ${this.reportingType} #${this.reportingId} | Loại: ${this.reportCategory} | Chi tiết: ${this.reportReason}`);
    
    // Simulate API call
    setTimeout(() => {
      // Clear data
      this.reportCategory = '';
      this.reportReason = '';

      // Close the report modal explicitly if needed (though data-bs-dismiss on button handles it)
      // Show Success Modal
      const successModalElement = document.getElementById('reportSuccessModal');
      if (successModalElement) {
        const successModal = bootstrap.Modal.getOrCreateInstance(successModalElement);
        successModal.show();
      }
    }, 300);
  }

  addToCart(): void {
    if (this.product && this.product.quantity > 0) {
      this.cartService.addToCart(this.product);
      alert('Đã thêm sản phẩm vào giỏ hàng thành công!');
    }
  }
}