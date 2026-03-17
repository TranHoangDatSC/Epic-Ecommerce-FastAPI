import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { Product, ProductImage } from '../../../core/models';
import { environment } from '../../../../environments/environment';

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

  constructor(private route: ActivatedRoute) {}

  ngOnInit(): void {
    // Get product from route data or service
    // For demo purposes, we'll assume product is loaded
    this.loadProduct();
  }

  private loadProduct(): void {
    // This would typically call a service to fetch product by ID
    // For this example, we'll create a mock product
    const mockProduct: Product = {
      product_id: 1,
      title: 'Laptop cu Dell Inspiron 15',
      description: 'Laptop Dell Inspiron 15 da qua su dung, cau hinh Core i5, RAM 8GB, SSD 256GB, man hinh 15.6 inch. Con bao hanh 6 thang.',
      price: 8500000,
      quantity: 3,
      category_id: 1,
      seller_id: 4,
      status: 1,
      view_count: 0,
      is_deleted: false,
      created_at: '2024-01-01T00:00:00Z',
      is_approved: true,
      product_images: [
        {
          image_id: 1,
          image_url: '/static/products/1_1_dell_laptop.jpg',
          alt_text: 'Dell Inspiron 15 front view',
          is_primary: true,
          display_order: 1
        },
        {
          image_id: 2,
          image_url: '/static/products/1_2_dell_laptop_side.jpg',
          alt_text: 'Dell Inspiron 15 side view',
          is_primary: false,
          display_order: 2
        }
      ]
    };

    this.product = mockProduct;
    this.setImages();
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
}