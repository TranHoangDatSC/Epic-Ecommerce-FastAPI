import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { environment } from '../../../../environments/environment';
import { UIService } from '../../../core/services/ui.service';

@Component({
  selector: 'app-product-manage',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: './product-manage.html',
  styleUrl: './product-manage.scss'
})
export class ProductManageComponent implements OnInit {
  private http = inject(HttpClient);
  private fb = inject(FormBuilder);
  private uiService = inject(UIService);
  private cdr = inject(ChangeDetectorRef);
  private apiUrl = environment.apiUrl;

  products: any[] = [];
  categories: any[] = [];
  productForm!: FormGroup;
  selectedFiles: File[] = [];
  
  currentStatus = 0;
  currentPage = 1;
  pageSize = 5;
  showModal = false;
  isEditMode = false;
  editingProductId: number | null = null;
  isSubmitting = false;
  isUpdatingStatus = false;
  totalItems: number = 0;

  ngOnInit() {
    this.initForm();
    this.loadProducts();
    this.loadCategories();
  }

  initForm() {
    this.productForm = this.fb.group({
      title: ['', [Validators.required, Validators.maxLength(255)]],
      description: [''],
      category_id: ['', Validators.required],
      price: ['', [Validators.required, Validators.min(1)]],
      quantity: ['', [Validators.required, Validators.min(1)]],
      video_url: [''],
      weight_grams: [''],
      d: [''], r: [''], c: [''],
      condition_rating: ['8', [Validators.required, Validators.min(1), Validators.max(10)]],
      warranty_months: ['0', Validators.min(0)],
      transfer_method: ['1', Validators.required]
    });
  }

  loadProducts() {
    this.http.get<any[]>(`${this.apiUrl}/products/seller/my-products`).subscribe({
      next: (data) => {
        this.products = data;
        this.updateTotal();
        this.cdr.detectChanges();
      }
    });
  }

  loadCategories() {
    this.http.get<any[]>(`${this.apiUrl}/categories`).subscribe({
      next: (data) => {
        this.categories = data;
        this.cdr.detectChanges();
      }
    });
  }

  getPrimaryImage(product: any): string {
    const primaryImage = product.product_images?.find((img: any) => img.is_primary);
    const raw = primaryImage ? primaryImage.image_url : (product.product_images?.[0]?.image_url || '');
    if (!raw) return 'assets/placeholder.jpg';
    if (raw.startsWith('/')) return `${environment.imageBaseUrl || 'http://localhost:8000'}${raw}`;
    return raw;
  }

  get filteredProducts() { return this.products.filter(p => p.status === this.currentStatus); }
  get pagedProducts() {
    const start = (this.currentPage - 1) * this.pageSize;
    return this.filteredProducts.slice(start, start + this.pageSize);
  }

  updateTotal() { this.totalItems = this.filteredProducts.length; }

  switchTab(s: number) {
    this.currentStatus = s;
    this.currentPage = 1;
    this.updateTotal();
    this.cdr.detectChanges();
  }

  changePage(page: number) {
    if (page >= 1 && page <= Math.ceil(this.filteredProducts.length / this.pageSize)) {
      this.currentPage = page;
    }
  }

  getStatusBadge(status: number): { class: string, label: string } {
    switch (status) {
      case 0: return { class: 'badge bg-warning text-dark', label: 'Chờ duyệt' };
      case 1: return { class: 'badge bg-success', label: 'Đã duyệt' };
      case 2: return { class: 'badge bg-danger', label: 'Từ chối' };
      case 3: return { class: 'badge bg-secondary', label: 'Ngừng bán' };
      default: return { class: 'badge bg-light text-dark', label: 'Không xác định' };
    }
  }

  openModal(p?: any) {
    this.isEditMode = !!p;
    this.editingProductId = p ? p.product_id : null;
    
    // Gán dữ liệu trước khi show modal để DOM không bị "lỏ"
    if (p) {
      const patchData = { ...p };
      if (p.dimensions && typeof p.dimensions === 'string' && p.dimensions.includes('x')) {
        const parts = p.dimensions.split('x');
        patchData.d = parts[0]; patchData.r = parts[1]; patchData.c = parts[2];
      }
      this.productForm.patchValue(patchData);
    } else {
      this.productForm.reset({ condition_rating: '8', warranty_months: '0', transfer_method: '1' });
      this.selectedFiles = [];
    }
    this.showModal = true;
  }

  onFileSelected(event: any) { if (event.target.files.length > 0) this.selectedFiles = Array.from(event.target.files); }

  get displayPrice(): string {
    const price = this.productForm.get('price')?.value;
    return price ? price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".") : '';
  }

  onPriceInput(event: any) {
    const rawValue = event.target.value.replace(/\./g, '');
    if (!isNaN(rawValue)) this.productForm.patchValue({ price: rawValue }, { emitEvent: false });
  }

  onSubmit() {
    if (this.productForm.invalid) {
      this.productForm.markAllAsTouched();
      this.uiService.showError('Vui lòng kiểm tra lại thông tin.', 'Cảnh báo');
      return;
    }
    if (!this.isEditMode && this.selectedFiles.length === 0) {
      this.uiService.showError('Vui lòng chọn ảnh.', 'Cảnh báo');
      return;
    }
    this.isSubmitting = true;
    const formData = new FormData();
    const formValue = this.productForm.value;
    const dimensions = `${formValue.d || 0}x${formValue.r || 0}x${formValue.c || 0}`;
    Object.keys(formValue).forEach(key => { if (!['d', 'r', 'c'].includes(key)) formData.append(key, formValue[key]); });
    formData.append('dimensions', dimensions);
    this.selectedFiles.forEach(file => formData.append('files', file));

    const obs = this.isEditMode ? this.http.put(`${this.apiUrl}/products/${this.editingProductId}`, { ...formValue, dimensions }) : this.http.post(`${this.apiUrl}/products`, formData);
    
    obs.subscribe({
      next: () => {
        this.uiService.showSuccess('Thành công', 'Thành công');
        this.closeModal();
        this.loadProducts();
      },
      error: (err) => { this.isSubmitting = false; this.uiService.showError(err.error?.message || 'Lỗi', 'Lỗi'); }
    });
  }

  updateStatus(product: any, newStatus: number) {
    if (this.isUpdatingStatus) return;
    this.isUpdatingStatus = true;
    this.http.patch(`${this.apiUrl}/products/${product.product_id}/status`, { new_status: newStatus }).subscribe({
      next: () => {
        this.loadProducts();
        this.isUpdatingStatus = false;
      },
      error: () => { this.isUpdatingStatus = false; }
    });
  }

  deleteProduct(id: number) {
    if (confirm('Xóa sản phẩm?')) this.http.delete(`${this.apiUrl}/products/${id}`).subscribe(() => this.loadProducts());
  }

  closeModal() {
    this.showModal = false;
    this.isSubmitting = false;
  }
}