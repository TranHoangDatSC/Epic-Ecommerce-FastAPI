import { Component, OnInit, ChangeDetectorRef, isDevMode } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ModeratorService } from '../../../shared/services/moderator.service';
import { ProductService } from '../../../shared/services/product.service';
import { CategoryService } from '../../../shared/services/category.service';
import { environment } from '../../../../environments/environment';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';

declare var bootstrap: any

@Component({
  selector: 'app-moderator-product-manage',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './product-manage.html',
  styleUrl: './product-manage.scss'
})
export class ModeratorProductManageComponent implements OnInit {
  products: any[] = [];
  isLoading = false;
  actionLoading = false;
  message: string | null = null;
  activeTab: 'pending' | 'approved' | 'rejected' = 'pending';
  selectedProduct: any = null;
  targetStatus: number | null = null;
  rejectionReason: string = '';
  category: any[] = [];
  categoryMap: Map<number, string> = new Map();
  userMap: Map<number, string> = new Map();
  isViewMode: boolean = false;

  currentPage: number = 1;
  pageSize: number = 5;

  constructor(
    private moderatorService: ModeratorService,
    private cdr: ChangeDetectorRef,
    private productService: ProductService,
    private categoryService: CategoryService,
    private sanitizer: DomSanitizer
  ) {}

  ngOnInit(): void {
    import('rxjs').then(rxjs => {
      rxjs.forkJoin({
        categories: this.categoryService.getCategories(),
        users: this.moderatorService.getUsers()
      }).subscribe(({ categories, users }) => {
        this.category = categories;
        users.forEach(u => this.userMap.set(u.user_id, u.username));
        this.loadProducts();
      });
    });
  }

  get paginatedProducts() {
    const start = (this.currentPage - 1) * this.pageSize;
    const end = start + this.pageSize;
    return this.products.slice(start, end);
  }

  get totalPages(): number {
    return Math.ceil(this.products.length / this.pageSize);
  }

  getVideoUrl(product: any): string | null {
    return product.video_url ? this.getFullUrl(product.video_url) : null;
  }

  loadProducts(): void {
    this.isLoading = true;
    const statusMap = { 'pending': 0, 'approved': 1, 'rejected': 2 };
    const status = statusMap[this.activeTab];

    this.productService.getProductsByStatus(status).subscribe({
      next: (data) => {
        this.category.forEach(c => this.categoryMap.set(c.category_id, c.name));

        this.products = (data || []).map(p => ({
          ...p,
          category_name: this.categoryMap.get(p.category_id) || 'Chưa phân loại',
          seller_name: this.userMap.get(p.seller_id) || 'User #' + p.seller_id,
          product_name: p.title || 'Sản phẩm không tên' 
        }));
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: () => { this.isLoading = false; }
    });
  }

  selectTab(tab: 'pending' | 'approved' | 'rejected'): void {
    this.activeTab = tab;
    this.currentPage = 1; 
    this.loadProducts();
  }


  updateStatus(product: any, targetStatus: 'approved' | 'rejected') {
    const statusMap = { 'approved': 1, 'rejected': 2 };
    const numericStatus = statusMap[targetStatus];
    let reason: string | undefined;

    if (targetStatus === 'rejected') {
      const input = prompt('Lý do');
      if (!input || input.trim() === '') {
          return;
      }
      reason = input;
    }

    this.actionLoading = true;
    this.productService.updateProductStatus(product.product_id, numericStatus, reason).subscribe({
      next: () => {
        this.message = `Đã cập nhật trạng thái sản phẩm thành công.`;
        this.actionLoading = false;
        this.loadProducts(); // Tải lại danh sách
      },
      error: (err) => {
        this.message = 'Lỗi cập nhật: ' + (err.error?.detail || 'Vui lòng thử lại.');
        this.actionLoading = false;
      }
    });
  }

  openModal(product: any, status: 'approved' | 'rejected', viewMode: boolean = false) {
    this.selectedProduct = product;
    this.isViewMode = viewMode;
    this.targetStatus = status === 'approved' ? 1 : 2;
    
    if (viewMode) {
      this.rejectionReason = product.reject_reason || 'Không có lý do.';
    } else {
      this.rejectionReason = '';
    }
    
    new bootstrap.Modal(document.getElementById('reasonModal')).show();
  }

  showFullReason(product: any) {
    this.openModal(product, 'rejected', true);
  }

  confirmAction() {
    if (this.targetStatus === 2 && !this.rejectionReason.trim()) {
      alert('Vui lòng nhập lý do!');
      return;
    }
    
    // Gọi API cập nhật
    this.productService.updateProductStatus(
      this.selectedProduct.product_id, 
      this.targetStatus!, 
      this.rejectionReason
    ).subscribe({
      next: () => {
        this.closeModal();
        this.loadProducts(); // <--- CỰC KỲ QUAN TRỌNG: Load lại để cập nhật video_url và images
        this.message = "Thao tác thành công!";
      },
      error: (err) => {
        alert("Lỗi: " + (err.error?.detail || "Không thể cập nhật"));
      }
    });
  }

  viewProductDetail(product: any) {
    this.selectedProduct = product;
    const modalEl = document.getElementById('productDetailModal');
    if (modalEl) {
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    } else {
        console.error("Không tìm thấy element productDetailModal trong HTML!");
    }
  }

  closeDetailModal() {
    const modalEl = document.getElementById('productDetailModal');
    const modal = bootstrap.Modal.getInstance(modalEl);
    if (modal) modal.hide();
  }

  currentPreviewImage: string | null = null;
  getFullUrl(url: string): string {
    if (!url) return 'assets/placeholder.jpg';
    
    let baseUrl = environment.imageBaseUrl;
    if (baseUrl.startsWith('https') && isDevMode()) {
      console.warn('Using HTTPS in local, may cause ERR_SSL error');
    }

    if (url.startsWith('/')) return `${baseUrl}${url}`;
    return url;
  }
  getPrimaryImage(product: any): string {
    const primary = product.product_images?.find((img: any) => img.is_primary);
    return this.getFullUrl(primary ? primary.image_url : (product.product_images?.[0]?.image_url || ''));
  }

  getSafeVideoUrl(url: string): SafeResourceUrl | string | null {
    if (!url) return null;
      const youtubeRegExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
      const match = url.match(youtubeRegExp);

      if (match && match[2].length === 11) {
          const embedUrl = `https://www.youtube.com/embed/${match[2]}`;
          return this.sanitizer.bypassSecurityTrustResourceUrl(embedUrl);
      }
      return this.getFullUrl(url);
  }

  isVideoType(url: string, type: 'youtube' | 'direct'): boolean {
    if (!url) return false;
    const isYoutube = /^(link_với_regex_youtube)/; 
    const checkYoutube = url.includes('youtube.com') || url.includes('youtu.be');
    return type === 'youtube' ? checkYoutube : !checkYoutube;
  }

  quickAction(status: 'approved' | 'rejected') {
    const modalDetail = bootstrap.Modal.getInstance(document.getElementById('productDetailModal'));
    modalDetail.hide();
    
    setTimeout(() => {
      this.openModal(this.selectedProduct, status);
    }, 400);
  }
  getRawVideoUrl(product: any): string {
    if (!product || !product.video_url) return '';
    if (product.video_url.includes('yout')) {
      return product.video_url;
    }
    return this.getFullUrl(product.video_url);
  }

  closeModal() {
    const modalEl = document.getElementById('reasonModal');
    const modal = bootstrap.Modal.getInstance(modalEl);
    modal.hide();
  }
}
