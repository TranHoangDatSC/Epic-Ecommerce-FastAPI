import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ModeratorService } from '../../../shared/services/moderator.service';

interface Product {
  product_id: number;
  title: string;
  description?: string;
  price: number;
  status: number;
  seller: {
    full_name: string;
  };
  category: {
    name: string;
  };
  product_images: Array<{
    image_url: string;
    is_primary: boolean;
  }>;
}

@Component({
  selector: 'app-product-check',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './product-check.html',
  styleUrl: './product-check.scss'
})
export class ProductCheckComponent implements OnInit {
  pendingProducts: Product[] = [];
  selectedProduct: Product | null = null;
  rejectReason: string = '';
  showRejectModal: boolean = false;
  processingProduct: number | null = null;

  constructor(private moderatorService: ModeratorService) {}

  ngOnInit() {
    this.loadPendingProducts();
  }

  loadPendingProducts() {
    this.moderatorService.getPendingProducts().subscribe({
      next: (products) => {
        this.pendingProducts = products;
      },
      error: (error) => {
        console.error('Error loading pending products:', error);
        // TODO: Show error message
      }
    });
  }

  approveProduct(productId: number) {
    if (this.processingProduct) return;

    this.processingProduct = productId;

    this.moderatorService.approveProduct(productId, 1).subscribe({
      next: () => {
        this.pendingProducts = this.pendingProducts.filter(p => p.product_id !== productId);
        this.processingProduct = null;
        // TODO: Show success message
      },
      error: (error) => {
        console.error('Error approving product:', error);
        this.processingProduct = null;
        // TODO: Show error message
      }
    });
  }

  openRejectModal(product: Product) {
    this.selectedProduct = product;
    this.rejectReason = '';
    this.showRejectModal = true;
  }

  closeRejectModal() {
    this.showRejectModal = false;
    this.selectedProduct = null;
    this.rejectReason = '';
  }

  rejectProduct() {
    if (!this.selectedProduct || !this.rejectReason.trim()) return;

    this.processingProduct = this.selectedProduct.product_id;

    this.moderatorService.approveProduct(this.selectedProduct.product_id, 2, this.rejectReason).subscribe({
      next: () => {
        this.pendingProducts = this.pendingProducts.filter(p => p.product_id !== this.selectedProduct!.product_id);
        this.closeRejectModal();
        this.processingProduct = null;
        // TODO: Show success message
      },
      error: (error) => {
        console.error('Error rejecting product:', error);
        this.processingProduct = null;
        // TODO: Show error message
      }
    });
  }

  getPrimaryImage(product: Product): string {
    const primaryImage = product.product_images.find(img => img.is_primary);
    return primaryImage ? primaryImage.image_url : (product.product_images[0]?.image_url || '/assets/images/placeholder.png');
  }

  getStatusBadge(status: number): { text: string, class: string } {
    switch (status) {
      case 0: return { text: 'Chờ duyệt', class: 'bg-warning' };
      case 1: return { text: 'Đã duyệt', class: 'bg-success' };
      case 2: return { text: 'Từ chối', class: 'bg-danger' };
      default: return { text: 'Không xác định', class: 'bg-secondary' };
    }
  }
}
