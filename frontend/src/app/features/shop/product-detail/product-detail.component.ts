import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, ActivatedRoute, Router } from '@angular/router';
import { Category, Product, ProductImage } from '../../../core/models';
import { environment } from '../../../../environments/environment';
import { ProductService } from '../../../shared/services/product.service';
import { CartService } from '../../../core/services/cart.service';
import { UIService } from '../../../core/services/ui.service';
import { AuthService } from '../../../core/services/auth.service';
import { CategoryService } from '../../../shared/services/category.service';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
declare var bootstrap: any;

@Component({
  selector: 'app-product-detail',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './product-detail.component.html',
  styleUrls: ['./product-detail.component.scss']
})
export class ProductDetailComponent implements OnInit {
  product: any | null = null;
  primaryImage: ProductImage | null = null;
  secondaryImages: ProductImage[] = [];
  imageBaseUrl = environment.imageBaseUrl;
  categories: Category[] = [];
  
  constructor(
    private route: ActivatedRoute,
    private productService: ProductService,
    public cartService: CartService,
    private uiService: UIService,
    private cdr: ChangeDetectorRef,
    private authService: AuthService,
    private categoryService: CategoryService,
    private router: Router,
    private sanitizer: DomSanitizer
  ) {}

  ngOnInit(): void {
    this.categoryService.getCategories().subscribe(cats => this.categories = cats);
    this.route.params.subscribe(params => {
      const id = +params['id'];
      if (id) {
        this.loadProduct(id);
      }
    });
  }

  getCategoryName(id: number): string {
    const cat = this.categories.find(c => c.category_id === id);
    return cat ? cat.name : 'Đang tải...';
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
        this.uiService.showError('Không thể tải thông tin sản phẩm.');
        this.cdr.detectChanges();
      }

    });
  }
  
  private setImages(): void {
    if (this.product?.product_images) {
      this.primaryImage = this.product.product_images.find((img: any) => img.is_primary) || null;
      this.secondaryImages = this.product.product_images.filter((img: any) => !img.is_primary);
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

  getSafeVideoUrl(url: string | undefined): SafeResourceUrl | string | null {
  if (!url) return null;
  const youtubeRegExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
  const match = url.match(youtubeRegExp);
  if (match && match[2].length === 11) {
    const embedUrl = `https://www.youtube.com/embed/${match[2]}`;
    return this.sanitizer.bypassSecurityTrustResourceUrl(embedUrl);
  }
  if (url.includes('drive.google.com')) {
    return url; 
  }
  return this.sanitizer.bypassSecurityTrustResourceUrl(url);
}

getVideoType(url: string | undefined): 'youtube' | 'drive' | 'direct' | 'none' {
  if (!url) return 'none';
  if (url.includes('youtube.com') || url.includes('youtu.be')) return 'youtube';
  if (url.includes('drive.google.com')) return 'drive';
  return 'direct';
}

  reportingType: 'product' | 'review' | null = null;
  reportingId: number | null = null;
  reportCategory: string = '';
  reportReason: string = '';
  couponCode: string = '';

  applyCoupon(): void {
    if (!this.couponCode.trim()) {
      this.uiService.showError('Vui lòng nhập mã giảm giá!');
      return;
    }
    this.uiService.showModal({
      title: 'Mã giảm giá',
      message: `Đang kiểm tra mã: ${this.couponCode}. Tính năng này sẽ sớm ra mắt!`,
      type: 'info'
    });
  }
  selectedVoucher: string = '';
  userRating: number = 5;
  commentText: string = '';
  
  onVoucherSelect() {
    this.couponCode = this.selectedVoucher;
  }

  submitReview() {
    if (!this.commentText.trim()) {
      this.uiService.showError('Vui lòng nhập nội dung đánh giá!');
      return;
    }
    // Logic gửi review lên Backend ở đây
    console.log('Gửi review:', { rating: this.userRating, content: this.commentText });
    this.uiService.showSuccess('Cảm ơn bạn đã đánh giá!');
    this.commentText = '';
  }

  confirmReport() {
    // Logic gửi báo cáo ở đây
    this.uiService.showSuccess('Báo cáo của bạn đã được gửi tới đội ngũ quản trị.');
    // Tự động đóng modal nếu cần (dùng bootstrap modal instance)
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
      this.uiService.showError('Vui lòng chọn lý do báo cáo!');
      return;
    }

    const typeLabel = this.reportingType === 'product' ? 'Sản phẩm' : 'Đánh giá';
    console.log(`Báo cáo ${this.reportingType} #${this.reportingId} | Loại: ${this.reportCategory} | Chi tiết: ${this.reportReason}`);
    setTimeout(() => {
      this.reportCategory = '';
      this.reportReason = '';
      const successModalElement = document.getElementById('reportSuccessModal');
      if (successModalElement) {
        const successModal = bootstrap.Modal.getOrCreateInstance(successModalElement);
        successModal.show();
      }
    }, 300);
  }

  addToCart(): void {
    if (!this.product) return;

    // 1. Kiểm tra đăng nhập (Giữ nguyên logic của bạn)
    if (!this.authService.isLoggedIn()) {
        const modalElement = document.getElementById('loginModal');
        if (modalElement) {
            const modal = (window as any).bootstrap.Modal.getOrCreateInstance(modalElement);
            modal.show();
        }
        return;
    }
    this.cartService.addToCart(this.product);
    this.router.navigate(['/customer/cart']); 
  }

  canAddToCart(): boolean {
    if (!this.product) return false;
    const inCart = this.cartService.getProductQuantityInCart(this.product.product_id);
    return this.product.quantity > 0 && inCart < this.product.quantity;
  }
}
