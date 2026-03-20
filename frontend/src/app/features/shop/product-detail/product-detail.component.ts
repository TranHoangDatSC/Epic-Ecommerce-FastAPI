import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { Product, ProductImage } from '../../../core/models';
import { environment } from '../../../../environments/environment';
import { ProductService } from '../../../shared/services/product.service';

@Component({
  selector: 'app-product-detail',
  standalone: true,
  imports: [CommonModule],
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

  reportProduct(): void {
    if (confirm('Bạn có muốn báo cáo sản phẩm này không?')) {
      alert('Đã gửi báo cáo sản phẩm. Cảm ơn bạn!');
    }
  }

  reportReview(reviewId: number): void {
    if (confirm('Bạn có muốn báo cáo đánh giá này không?')) {
      alert(`Đã gửi báo cáo đánh giá #${reviewId}. Cảm ơn bạn!`);
    }
  }
}