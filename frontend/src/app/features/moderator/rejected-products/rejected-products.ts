import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ModeratorService } from '../../../shared/services/moderator.service';

interface RejectedProduct {
  product_id: number;
  title: string;
  description?: string;
  price: number;
  status: number;
  rejection_reason: string;
  rejected_at: string;
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
  selector: 'app-rejected-products',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './rejected-products.html',
  styleUrl: './rejected-products.scss'
})
export class RejectedProductsComponent implements OnInit {
  rejectedProducts: RejectedProduct[] = [];
  searchTerm: string = '';
  selectedCategory: string = '';
  categories: string[] = [];

  constructor(private moderatorService: ModeratorService) {}

  ngOnInit() {
    this.loadRejectedProducts();
  }

  loadRejectedProducts() {
    this.moderatorService.getRejectedProducts().subscribe({
      next: (products) => {
        this.rejectedProducts = products;
        this.extractCategories();
      },
      error: (error) => {
        console.error('Error loading rejected products:', error);
      }
    });
  }

  extractCategories() {
    const categorySet = new Set(this.rejectedProducts.map(p => p.category.name));
    this.categories = Array.from(categorySet).sort();
  }

  get filteredProducts(): RejectedProduct[] {
    return this.rejectedProducts.filter(product => {
      const matchesSearch = !this.searchTerm ||
        product.title.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        product.seller.full_name.toLowerCase().includes(this.searchTerm.toLowerCase());

      const matchesCategory = !this.selectedCategory || product.category.name === this.selectedCategory;

      return matchesSearch && matchesCategory;
    });
  }

  getPrimaryImage(product: RejectedProduct): string {
    const primaryImage = product.product_images.find(img => img.is_primary);
    return primaryImage ? primaryImage.image_url : (product.product_images[0]?.image_url || '/images/placeholder.png');
  }

  clearFilters() {
    this.searchTerm = '';
    this.selectedCategory = '';
  }

  resubmitProduct(productId: number) {
    // Logic to allow resubmission or appeal
    console.log('Resubmit product:', productId);
  }
}