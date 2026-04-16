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
  
  // States
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
      price: ['', [Validators.required, Validators.min(1)]], // Vẫn để số nguyên cho API
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
      }, 
      error: (err) => {
        this.uiService.showError('Không thể tải danh sách sản phẩm', 'Lỗi');
        this.cdr.detectChanges();
      }
    });
  }

  loadCategories() {
    this.http.get<any[]>(`${this.apiUrl}/categories`).subscribe({
      next: (data) => { this.categories = data; this.cdr.detectChanges(); }
    });
  }

  getPrimaryImage(product: any): string {
    const primaryImage = product.product_images?.find((img: any) => img.is_primary);
    const raw = primaryImage ? primaryImage.image_url : (product.product_images?.[0]?.image_url || '');
    
    if (!raw) {
      return 'assets/placeholder.jpg'; 
    }

    if (raw.startsWith('/')) {
      const base = environment.imageBaseUrl || 'http://localhost:8000';
      return `${base}${raw}`;
    }
    
    return raw;
  }

  // --- UI Helpers ---
  get filteredProducts() {
    return this.products.filter(p => p.status === this.currentStatus);
  }

  get pagedProducts() {
    const start = (this.currentPage - 1) * this.pageSize;
    return this.filteredProducts.slice(start, start + this.pageSize);
  }

  updateTotal() {
    this.totalItems = this.products.filter(p => p.status === this.currentStatus).length;
  }

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
    this.showModal = true;
    this.isEditMode = !!p;
    this.editingProductId = p ? p.product_id : null;
    
    if (p) {
      const patchData = { ...p };
      // Nếu dimensions là "10x20x30", tách nó ra
      if (p.dimensions && p.dimensions.includes('x')) {
        const parts = p.dimensions.split('x');
        patchData.d = parts[0];
        patchData.r = parts[1];
        patchData.c = parts[2];
      }
      this.productForm.patchValue(patchData);
    } else {
      this.productForm.reset({ condition_rating: '8', warranty_months: '0', transfer_method: '1' });
      this.selectedFiles = [];
    }
  }

  onFileSelected(event: any) {
    if (event.target.files.length > 0) this.selectedFiles = Array.from(event.target.files);
  }

  get displayPrice(): string {
    const price = this.productForm.get('price')?.value;
    return price ? price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".") : '';
  } 

  onPriceInput(event: any) {
    const rawValue = event.target.value.replace(/\./g, ''); 
    if (!isNaN(rawValue)) {
      this.productForm.patchValue({ price: rawValue }, { emitEvent: false });
    }
  }

  onSubmit() {
    if (this.productForm.invalid) { 
      this.productForm.markAllAsTouched(); 
      this.uiService.showError('Vui lòng kiểm tra lại thông tin.', 'Cảnh báo');
      this.cdr.detectChanges();
      return; 
    }

    if (!this.isEditMode && this.selectedFiles.length === 0) {
      this.uiService.showError('Vui lòng chọn ít nhất 1 ảnh sản phẩm.', 'Cảnh báo');
      return;
    }

    this.isSubmitting = true;
    const formData = new FormData();
    const formValue = this.productForm.value;
    const dimensions = `${formValue.d || 0}x${formValue.r || 0}x${formValue.c || 0}`;
    Object.keys(formValue).forEach(key => {
      if (['d', 'r', 'c'].includes(key)) return; 
      const val = formValue[key];
      if (val !== null) formData.append(key, val);
    });
    formData.append('dimensions', dimensions);
    this.selectedFiles.forEach(file => formData.append('files', file));
        
    const payload = { ...formValue, dimensions };
    delete payload.d; delete payload.r; delete payload.c; 

    if (this.isEditMode) {
      this.http.put(`${this.apiUrl}/products/${this.editingProductId}`, payload).subscribe({
        next: () => { 
          this.uiService.showSuccess('Cập nhật thành công', 'Thành công'); 
          this.closeModal(); 
          this.cdr.detectChanges(); 
        },
        error: (err) => { 
          this.isSubmitting = false; 
          this.uiService.showError(err.error?.message || 'Lỗi cập nhật', 'Lỗi');
          this.cdr.detectChanges();
        }
      });
    } else {
      this.http.post(`${this.apiUrl}/products`, formData).subscribe({
        next: () => { 
          this.uiService.showSuccess('Đăng sản phẩm thành công', 'Thành công'); 
          this.closeModal(); 
          this.cdr.detectChanges(); 
        },
        error: (err) => { 
          this.isSubmitting = false; 
          this.uiService.showError(err.error?.message || 'Lỗi đăng sản phẩm', 'Lỗi');
          this.cdr.detectChanges();
        }
      });
    }
  }

  updateStatus(product: any, newStatus: number) {
    if (this.isUpdatingStatus) return;
    
    this.isUpdatingStatus = true;
    this.http.patch(`${this.apiUrl}/products/${product.product_id}/status`, { 
      new_status: newStatus 
    }).subscribe({
      next: () => {
        // 1. Tải lại danh sách để reset trạng thái pagedProducts
        this.loadProducts(); 
        this.uiService.showSuccess('Đã cập nhật trạng thái', 'Thành công');
      },
      error: (err) => {
        this.uiService.showError(err.error?.message || 'Không thể cập nhật', 'Lỗi');
      },
      complete: () => {
        this.isUpdatingStatus = false;
        this.cdr.detectChanges();
      }
    });
  }

  deleteProduct(id: number) {
    if (confirm('Xóa sản phẩm?')) {
      this.http.delete(`${this.apiUrl}/products/${id}`).subscribe(() => this.loadProducts());
    }
  }

  closeModal() {
    this.showModal = false;
    this.isSubmitting = false; 
    this.selectedFiles = [];   
    this.productForm.reset({   
      condition_rating: '8', 
      warranty_months: '0', 
      transfer_method: '1' 
    });
    this.cdr.detectChanges();
  }
}