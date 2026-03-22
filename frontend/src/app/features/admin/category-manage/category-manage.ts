import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AdminService } from '../../../shared/services/admin.service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-category-manage',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './category-manage.html',
  styleUrl: './category-manage.scss'
})
export class CategoryManageComponent implements OnInit {
  categories: any[] = [];
  isLoading = false;
  showModal = false;
  editingCategory: any = null;
  categoryForm = {
    name: '',
    description: '',
    parent_id: null as number | null,
    is_active: true
  };

  constructor(private adminService: AdminService) {}

  ngOnInit(): void {
    this.loadCategories();
  }

  loadCategories() {
    this.isLoading = true;
    this.adminService.getCategories(false).subscribe({
      next: (data) => {
        this.categories = data;
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error loading categories:', err);
        this.isLoading = false;
      }
    });
  }

  openModal(category: any = null) {
    this.editingCategory = category;
    if (category) {
      this.categoryForm = {
        name: category.name,
        description: category.description,
        parent_id: category.parent_id,
        is_active: category.is_active !== undefined ? category.is_active : true
      };
    } else {
      this.categoryForm = { name: '', description: '', parent_id: null, is_active: true };
    }
    this.showModal = true;
  }

  closeModal() {
    this.showModal = false;
    this.editingCategory = null;
  }

  saveCategory() {
    if (this.editingCategory) {
      this.adminService.updateCategory(this.editingCategory.category_id, this.categoryForm).subscribe(() => {
        this.loadCategories();
        this.closeModal();
      });
    } else {
      this.adminService.createCategory(this.categoryForm).subscribe(() => {
        this.loadCategories();
        this.closeModal();
      });
    }
  }

  deleteCategory(id: number) {
    if (confirm('Are you sure you want to delete this category? (Soft delete)')) {
      this.adminService.deleteCategory(id).subscribe(() => this.loadCategories());
    }
  }
}
