import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { ProductService } from '../../shared/services/product.service';
import { CategoryService } from '../../shared/services/category.service';
import { Product, Category } from '../../core/models';

@Component({
  selector: 'app-shop',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './shop.html',
  styleUrls: ['./shop.scss']
})
export class ShopComponent implements OnInit {
  products: Product[] = [];
  categories: Category[] = [];
  currentPage = 1;
  totalPages = 1;
  itemsPerPage = 9;
  loading = false;
  searchQuery = '';
  selectedCategoryId: number | null = null;

  constructor(
    private productService: ProductService,
    private categoryService: CategoryService
  ) {}

  ngOnInit() {
    this.loadCategories();
    this.loadProducts();
  }

  loadCategories() {
    this.categoryService.getCategories().subscribe({
      next: (categories) => {
        this.categories = categories;
      },
      error: (error) => {
        console.error('Error loading categories:', error);
      }
    });
  }

  loadProducts() {
    this.loading = true;
    const skip = (this.currentPage - 1) * this.itemsPerPage;

    this.productService.getProducts({
      skip,
      limit: this.itemsPerPage,
      search: this.searchQuery || undefined,
      category_id: this.selectedCategoryId || undefined,
      sort_by: 'created_at'
    }).subscribe({
      next: (products) => {
        this.products = products;
        // Assuming the API returns all products, we need to calculate total pages
        // In a real scenario, the API should return total count
        // For now, if we get less than itemsPerPage, it's the last page
        if (products.length < this.itemsPerPage) {
          this.totalPages = this.currentPage;
        } else {
          // We need to estimate or get total count from API
          // For simplicity, assume there are more pages
          this.totalPages = this.currentPage + 1;
        }
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading products:', error);
        this.loading = false;
      }
    });
  }

  onSearch() {
    this.currentPage = 1;
    this.loadProducts();
  }

  onCategoryChange() {
    this.currentPage = 1;
    this.loadProducts();
  }

  onPageChange(page: number) {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
      this.loadProducts();
    }
  }

  getPages(): number[] {
    const pages: number[] = [];
    const start = Math.max(1, this.currentPage - 2);
    const end = Math.min(this.totalPages, this.currentPage + 2);

    for (let i = start; i <= end; i++) {
      pages.push(i);
    }
    return pages;
  }

  getPrimaryImage(product: Product): string {
    const primaryImage = product.product_images?.find(img => img.is_primary);
    return primaryImage ? primaryImage.image_url : (product.product_images?.[0]?.image_url || '/assets/placeholder.jpg');
  }
}
