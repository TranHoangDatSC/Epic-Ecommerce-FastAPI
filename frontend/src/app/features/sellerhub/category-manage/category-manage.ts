import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
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
  skip = 0;
  limit = 5;
  isLoading = false;
  showModal = false;
  editingCategory: any = null;
  activeTab: 'active' | 'trash' = 'active';

  get pagedCategories(): any[] {
    return this.categories.slice(this.skip, this.skip + this.limit);
  }
  
  categoryForm = {
    name: '',
    description: '',
    parent_id: null as number | null,
    is_active: true
  };

  constructor(
    private adminService: AdminService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadCategoriesMock();
  }
loadCategoriesMock() {
  this.categories = [
    {
      category_id: 1,
      name: 'Điện thoại',
      description: 'Các loại smartphone',
      parent_id: null,
      is_active: true,
      is_deleted: false,
    },
    {
      category_id: 2,
      name: 'Laptop',
      description: 'Máy tính xách tay',
      parent_id: null,
      is_active: true,
      is_deleted: false
    },
    {
      category_id: 3,
      name: 'iPhone',
      description: 'Apple phone',
      parent_id: 1,
      is_active: true,
      is_deleted: false
    },
    {
      category_id: 4,
      name: 'Samsung',
      description: 'Samsung phone',
      parent_id: 1,
      is_active: false,
      is_deleted: false
    },
    {
      category_id: 5,
      name: 'Đã xóa demo',
      description: 'Test trash',
      parent_id: null,
      is_active: false,
      is_deleted: true
    }
  ];

  // xử lý giống logic cũ
  if (this.activeTab === 'trash') {
    this.categories = this.categories.filter(cat => cat.is_deleted);
  } else {
    this.categories = this.categories
      .filter(cat => !cat.is_deleted)
      .sort((a, b) => (a.is_active === b.is_active ? 0 : a.is_active ? -1 : 1));
  }
}
  loadCategories() {
    this.isLoading = true;
    // Xóa danh sách cũ để UI reset trạng thái, tránh nhầm lẫn dữ liệu
    this.categories = []; 
    
    const includeDeleted = this.activeTab === 'trash';
    
    // Gọi API: Tham số 1 (false) cho active_only để lấy cả category bị ẩn
    // Tham số 2 (includeDeleted) để lấy dữ liệu từ thùng rác khi cần
    this.adminService.getCategories(false, includeDeleted).subscribe({
      next: (data) => {
        if (this.activeTab === 'trash') {
          // Lọc các mục đã xóa mềm
          this.categories = data.filter(cat => cat.is_deleted === true);
        } else {
          // Lọc các mục chưa xóa và sắp xếp: cái nào Active lên đầu
          this.categories = data.filter(cat => !cat.is_deleted)
            .sort((a, b) => {
              if (a.is_active === b.is_active) return 0;
              return a.is_active ? -1 : 1;
            });
        }

        if (this.skip >= this.categories.length) {
          this.skip = 0;
        }
        
        this.isLoading = false;
        // FIX: Ép Angular vẽ lại giao diện ngay lập tức
        this.cdr.detectChanges(); 
      },
      error: (err) => {
        console.error('Lỗi khi tải danh mục:', err);
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  switchTab(tab: 'active' | 'trash') {
    this.activeTab = tab;
    this.skip = 0;
    this.loadCategories();
  }

  nextPage(): void {
    if (this.skip + this.limit < this.categories.length) {
      this.skip += this.limit;
    }
  }

  prevPage(): void {
    if (this.skip >= this.limit) {
      this.skip -= this.limit;
    }
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
      this.categoryForm = { 
        name: '', 
        description: '', 
        parent_id: null, 
        is_active: true 
      };
    }
    this.showModal = true;
  }

  closeModal() {
    this.showModal = false;
    this.editingCategory = null;
  }

  saveCategory() {
    if (this.editingCategory) {
      this.adminService.updateCategory(this.editingCategory.category_id, this.categoryForm).subscribe({
        next: () => {
          this.loadCategories();
          this.closeModal();
        },
        error: (err) => console.error('Error updating category:', err)
      });
    } else {
      this.adminService.createCategory(this.categoryForm).subscribe({
        next: () => {
          this.loadCategories();
          this.closeModal();
        },
        error: (err) => console.error('Error creating category:', err)
      });
    }
  }

  deleteCategory(id: number) {
    if (confirm('Bạn có chắc chắn muốn xóa danh mục này? (Xóa mềm)')) {
      this.adminService.deleteCategory(id).subscribe({
        next: () => this.loadCategories(),
        error: (err) => console.error('Error deleting category:', err)
      });
    }
  }

  restoreCategory(id: number) {
    if (confirm('Khôi phục danh mục này về danh sách hoạt động?')) {
      this.adminService.restoreCategory(id).subscribe({
        next: () => this.loadCategories(),
        error: (err) => console.error('Error restoring category:', err)
      });
    }
  }

  hardDeleteCategory(id: number) {
    if (confirm('CẢNH BÁO: Hành động này sẽ xóa vĩnh viễn và không thể hoàn tác!')) {
      this.adminService.hardDeleteCategory(id).subscribe({
        next: () => this.loadCategories(),
        error: (err) => console.error('Error hard deleting category:', err)
      });
    }
  }
}