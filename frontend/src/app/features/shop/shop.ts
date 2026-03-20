import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { ProductService } from '../../shared/services/product.service';
import { CategoryService } from '../../shared/services/category.service';
import { Product, Category } from '../../core/models';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-shop',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './shop.html',
  styleUrls: ['./shop.scss']
})
export class ShopComponent implements OnInit {
  allProducts: Product[] = [];
  products: Product[] = [];
  filteredProducts: Product[] = [];
  categories: Category[] = [];
  categoryCounts: Record<number, number> = {};

  currentPage = 1;
  totalPages = 1;
  itemsPerPage = 9;

  loading = false;
  searchQuery = '';
  selectedCategoryId: number | null = null;
  priceMin: number | null = null;
  priceMax: number | null = null;

  constructor(
    private productService: ProductService,
    private categoryService: CategoryService,
    private cdr: ChangeDetectorRef,
    private router: Router
  ) {
    // Reload data if navigating back to /shop (handles clicking header link again)
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd),
      filter(event => (event as NavigationEnd).urlAfterRedirects === '/shop')
    ).subscribe(() => {
      this.initialLoad();
    });
  }

  ngOnInit() {
    this.initialLoad();
  }

  private initialLoad() {
    this.loadCategories();
    this.loadProducts();
  }

  loadCategories() {
    this.categoryService.getCategories().subscribe({
      next: (categories) => {
        this.categories = categories;
        this.cdr.detectChanges();
      },
      error: (error) => {
        console.error('Error loading categories:', error);
      }
    });
  }

  loadProducts() {
    this.loading = true;

    // Load all approved products to support filtering and counts
    this.productService.getProducts({
      skip: 0,
      limit: 1000,
      sort_by: 'created_at'
    }).subscribe({
      next: (products) => {
        this.allProducts = products;
        this.computeCategoryCounts();
        this.applyFilters();
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: (error) => {
        console.error('Error loading products:', error);
        this.loading = false;
      }
    });
  }

  computeCategoryCounts() {
    this.categoryCounts = {};
    for (const product of this.allProducts) {
      if (!this.categoryCounts[product.category_id]) {
        this.categoryCounts[product.category_id] = 0;
      }
      this.categoryCounts[product.category_id] += 1;
    }
  }

  applyFilters() {
    const min = this.priceMin ?? 0;
    const max = this.priceMax ?? Number.MAX_SAFE_INTEGER;

    this.filteredProducts = this.allProducts.filter((product) => {
      const matchesSearch = this.searchQuery
        ? product.title.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          (product.description || '').toLowerCase().includes(this.searchQuery.toLowerCase())
        : true;

      const matchesCategory = this.selectedCategoryId
        ? product.category_id === this.selectedCategoryId
        : true;

      const price = Number(product.price);
      const matchesPrice = price >= min && price <= max;

      return matchesSearch && matchesCategory && matchesPrice;
    });

    this.totalPages = Math.max(1, Math.ceil(this.filteredProducts.length / this.itemsPerPage));
    this.currentPage = 1;
    this.updatePageProducts();
  }

  updatePageProducts() {
    const start = (this.currentPage - 1) * this.itemsPerPage;
    const end = start + this.itemsPerPage;
    this.products = this.filteredProducts.slice(start, end);
  }

  onSearch() {
    this.applyFilters();
  }

  onCategoryChange(categoryId: number | null = null) {
    this.selectedCategoryId = categoryId;
    this.applyFilters();
  }

  onPriceFilter() {
    this.applyFilters();
  }

  onPageChange(page: number) {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
      this.updatePageProducts();
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
    const raw = primaryImage ? primaryImage.image_url : (product.product_images?.[0]?.image_url || '');

    if (!raw) {
      return 'https://via.placeholder.com/350x250?text=No+Image';
    }

    // If URL is relative (served by backend), prefix with base URL
    if (raw.startsWith('/')) {
      const base = environment.imageBaseUrl.replace(/\/+$/, '');
      const trimmed = raw.startsWith('/') ? raw : `/${raw}`;
      return `${base}${trimmed}`;
    }

    return raw;
  }

  formatPrice(value: number | string): string {
    const price = typeof value === 'string' ? Number(value) : value;
    if (!Number.isFinite(price)) {
      return '0 ₫';
    }
    return price.toLocaleString('vi-VN', { style: 'currency', currency: 'VND' });
  }
}
