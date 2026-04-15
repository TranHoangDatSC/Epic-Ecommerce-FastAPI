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

  products: any[] = [];
  categories: any[] = [];
  
  productForm!: FormGroup;
  selectedFiles: File[] = [];
  isSubmitting = false;
  showCreateModal = false;

  private apiUrl = environment.apiUrl;

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
      dimensions: [''],
      condition_rating: ['8', [Validators.required, Validators.min(1), Validators.max(10)]],
      warranty_months: ['0', Validators.min(0)],
      transfer_method: ['1', Validators.required]
    });
  }

  loadProducts() {
    this.http.get<any[]>(`${this.apiUrl}/products/seller/my-products`).subscribe({
      next: (data) => {
        this.products = data;
        this.cdr.detectChanges();
      },
      error: (err) => console.error('Error loading products', err)
    });
  }

  loadCategories() {
    this.http.get<any[]>(`${this.apiUrl}/categories`).subscribe({
      next: (data) => {
        this.categories = data;
        this.cdr.detectChanges();
      },
      error: (err) => console.error('Error loading categories', err)
    });
  }

  getStatusBadge(status: number) {
    switch (status) {
      case 0: return { class: 'badge bg-warning text-dark', label: 'Chờ duyệt' };
      case 1: return { class: 'badge bg-success', label: 'Đã duyệt' };
      case 2: return { class: 'badge bg-danger', label: 'Từ chối' };
      case 3: return { class: 'badge bg-secondary', label: 'Hết hàng' };
      default: return { class: 'badge bg-light text-dark', label: 'Không xác định' };
    }
  }

  onFileSelected(event: any) {
    if (event.target.files.length > 0) {
      this.selectedFiles = Array.from(event.target.files);
    }
  }

  openCreateModal() {
    this.productForm.reset({
      condition_rating: '8',
      warranty_months: '0',
      transfer_method: '1'
    });
    this.selectedFiles = [];
    this.showCreateModal = true;
  }

  closeCreateModal() {
    this.showCreateModal = false;
  }

  onSubmit() {
    if (this.productForm.invalid) {
      this.productForm.markAllAsTouched();
      return;
    }
    
    if (this.selectedFiles.length === 0) {
      this.uiService.showError('Vui lòng chọn ít nhất 1 hình ảnh sản phẩm.', 'Lỗi');
      return;
    }

    this.isSubmitting = true;
    const formData = new FormData();
    
    Object.keys(this.productForm.value).forEach(key => {
      const value = this.productForm.value[key];
      if (value !== null && value !== '') {
        formData.append(key, value);
      }
    });

    this.selectedFiles.forEach(file => {
      formData.append('files', file);
    });

    this.http.post(`${this.apiUrl}/products`, formData).subscribe({
      next: (res) => {
        this.uiService.showSuccess('Đăng sản phẩm thành công. Đang chờ quản trị viên duyệt.', 'Thành công');
        this.isSubmitting = false;
        this.closeCreateModal();
        this.loadProducts();
      },
      error: (err) => {
        this.isSubmitting = false;
        this.uiService.showError('Đã xảy ra lỗi khi đăng sản phẩm. Vui lòng thử lại.', 'Lỗi');
      }
    });
  }

  deleteProduct(id: number) {
    if (confirm('Bạn có chắc chắn muốn xóa sản phẩm này không?')) {
      this.http.delete(`${this.apiUrl}/products/${id}`).subscribe({
        next: () => {
          this.uiService.showSuccess('Đã xóa sản phẩm.', 'Thành công');
          this.loadProducts();
        },
        error: () => this.uiService.showError('Không thể xóa sản phẩm.', 'Lỗi')
      });
    }
  }
}
