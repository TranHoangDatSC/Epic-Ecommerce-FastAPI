import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, ActivatedRoute } from '@angular/router';
import { Product, ProductImage } from '../../../core/models';
import { environment } from '../../../../environments/environment';
import { ProductService } from '../../../shared/services/product.service';

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
    return `${this.imageBaseUrl}${imageUrl}`;
  }

  setPrimaryImage(image: ProductImage): void {
    this.primaryImage = image;
  }

  reportingType: 'product' | 'review' | null = null;
  reportingId: number | null = null;
  reportReason: string = '';

  reportProduct(): void {
    this.reportingType = 'product';
    this.reportingId = this.product?.product_id || null;
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
    this.reportReason = '';
    const modalElement = document.getElementById('reportModal');
    if (modalElement) {
      const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
      modal.show();
    }
  }

  submitReport(): void {
    if (!this.reportReason.trim()) {
      alert('Vui lòng nhập lý do báo cáo!');
      return;
    }

    const typeLabel = this.reportingType === 'product' ? 'Sản phẩm' : 'Đánh giá';
    console.log(`Báo cáo ${this.reportingType} #${this.reportingId} với lý do: ${this.reportReason}`);
    
    // Simulate API call
    setTimeout(() => {
      alert(`Đã gửi báo cáo ${typeLabel}. Cảm ơn bạn đã hỗ trợ chúng tôi!`);
      this.reportReason = '';
      // Close modal... usually handled by [data-bs-dismiss]
    }, 500);
  }
}