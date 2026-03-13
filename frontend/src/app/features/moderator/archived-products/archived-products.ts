import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ModeratorService } from '../../../shared/services/moderator.service';

interface ArchivedProduct {
  product_id: number;
  title: string;
  description?: string;
  price: number;
  status: number;
  archived_at: string;
  archive_reason: string;
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
  selector: 'app-archived-products',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './archived-products.html',
  styleUrl: './archived-products.scss'
})
export class ArchivedProductsComponent implements OnInit {
  archivedProducts: ArchivedProduct[] = [];
  searchTerm: string = '';
  selectedCategory: string = '';
  categories: string[] = [];

  constructor(private moderatorService: ModeratorService) {}

  ngOnInit() {
    this.loadArchivedProducts();
  }

  loadArchivedProducts() {
    this.moderatorService.getArchivedProducts().subscribe({
      next: (products) => {
        this.archivedProducts = products;
        this.extractCategories();
      },
      error: (error) => {
        console.error('Error loading archived products:', error);
      }
    });
  }

  extractCategories() {
    const categorySet = new Set(this.archivedProducts.map(p => p.category.name));
    this.categories = Array.from(categorySet).sort();
  }

  get filteredProducts(): ArchivedProduct[] {
    return this.archivedProducts.filter(product => {
      const matchesSearch = !this.searchTerm ||
        product.title.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        product.seller.full_name.toLowerCase().includes(this.searchTerm.toLowerCase());

      const matchesCategory = !this.selectedCategory || product.category.name === this.selectedCategory;

      return matchesSearch && matchesCategory;
    });
  }

  getPrimaryImage(product: ArchivedProduct): string {
    const primaryImage = product.product_images.find(img => img.is_primary);
    return primaryImage ? primaryImage.image_url : (product.product_images[0]?.image_url || '/images/placeholder.png');
  }

  restoreProduct(productId: number) {
    // Logic to restore archived product
    console.log('Restore product:', productId);
  }

  clearFilters() {
    this.searchTerm = '';
    this.selectedCategory = '';
  }
}