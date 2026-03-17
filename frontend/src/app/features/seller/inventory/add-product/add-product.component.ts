import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ProductService } from '../../../../shared/services/product.service';
import { CategoryService } from '../../../../shared/services/category.service';
import { Product, Category } from '../../../../core/models';

@Component({
  selector: 'app-add-product',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './add-product.component.html',
  styleUrls: ['./add-product.component.scss']
})
export class AddProductComponent {
  productForm: FormGroup;
  categories: Category[] = [];
  selectedFiles: File[] = [];
  isSubmitting = false;

  constructor(
    private fb: FormBuilder,
    private productService: ProductService,
    private categoryService: CategoryService,
    public router: Router
  ) {
    this.productForm = this.fb.group({
      category_id: ['', Validators.required],
      title: ['', [Validators.required, Validators.minLength(1), Validators.maxLength(255)]],
      description: [''],
      price: ['', [Validators.required, Validators.min(0)]],
      quantity: ['', [Validators.required, Validators.min(0)]],
      video_url: [''],
      weight_grams: [''],
      dimensions: [''],
      condition_rating: ['', [Validators.min(1), Validators.max(10)]],
      warranty_months: [0, Validators.min(0)]
    });
  }

  ngOnInit(): void {
    this.loadCategories();
  }

  loadCategories(): void {
    this.categoryService.getCategories().subscribe({
      next: (categories: Category[]) => {
        this.categories = categories;
      },
      error: (error: any) => {
        console.error('Error loading categories:', error);
      }
    });
  }

  onFileSelected(event: any): void {
    const files = event.target.files;
    if (files) {
      this.selectedFiles = Array.from(files);
    }
  }

  removeFile(index: number): void {
    this.selectedFiles.splice(index, 1);
  }

  isFormValid(): boolean {
    return this.productForm.valid && this.selectedFiles.length > 0;
  }

  onSubmit(): void {
    if (!this.isFormValid()) {
      return;
    }

    this.isSubmitting = true;

    const formData = new FormData();

    // Add form fields
    Object.keys(this.productForm.value).forEach(key => {
      const value = this.productForm.value[key];
      if (value !== null && value !== undefined && value !== '') {
        formData.append(key, value.toString());
      }
    });

    // Add files
    this.selectedFiles.forEach((file, index) => {
      formData.append('files', file);
    });

    this.productService.createProduct(formData).subscribe({
      next: (product: Product) => {
        this.isSubmitting = false;
        this.router.navigate(['/seller/inventory']);
      },
      error: (error: any) => {
        this.isSubmitting = false;
        console.error('Error creating product:', error);
        // Handle error (show toast, etc.)
      }
    });
  }

  getFilePreviewUrl(file: File): string {
    return URL.createObjectURL(file);
  }
}