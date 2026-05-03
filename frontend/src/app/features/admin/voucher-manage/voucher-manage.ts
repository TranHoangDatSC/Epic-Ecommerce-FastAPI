import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AdminService } from '../../../shared/services/admin.service';

@Component({
  selector: 'app-voucher-manage',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './voucher-manage.html',
  styleUrl: './voucher-manage.scss' // Dùng chung style với Category
})
export class VoucherManageComponent implements OnInit {
  vouchers: any[] = [];
  allVouchers: any[] = [];
  isLoading = false;
  showModal = false;
  editingVoucher: any = null;
  activeTab: 'active' | 'trash' = 'active';
  searchTerm: string = '';
  
  // Phân trang
  skip = 0;
  limit = 5;

  voucherForm = {
    code: '',
    description: '',
    discount_type: 0, // 0: Fixed, 1: Percentage
    discount_value: 0,
    max_usage: 100,
    min_order_amount: 0,
    valid_from: '',
    valid_to: '',
    is_active: true
  };

  constructor(private adminService: AdminService, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.loadVouchers();
  }

  loadVouchers() {
    this.isLoading = true;
    this.adminService.getVouchers().subscribe({
      next: (data) => {
        this.allVouchers = data;
        this.applyFilterAndTab();
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Lỗi tải voucher:', err);
        this.isLoading = false;
      }
    });
  }

  applyFilterAndTab() {
    let filtered = this.allVouchers;
    
    // Tab Filter
    if (this.activeTab === 'trash') {
      filtered = filtered.filter(v => v.is_deleted);
    } else {
      filtered = filtered.filter(v => !v.is_deleted);
    }

    // Search Filter
    if (this.searchTerm.trim()) {
      const term = this.searchTerm.toLowerCase();
      filtered = filtered.filter(v => v.code.toLowerCase().includes(term) || v.description?.toLowerCase().includes(term));
    }

    this.vouchers = filtered;
  }

  get pagedVouchers() {
    return this.vouchers.slice(this.skip, this.skip + this.limit);
  }

  // Logic Modal
  openModal(voucher: any = null) {
    this.editingVoucher = voucher;
    if (voucher) {
      this.voucherForm = { 
        ...voucher,
        // Chuyển format date ISO sang datetime-local cho input
        valid_from: voucher.valid_from.substring(0, 16),
        valid_to: voucher.valid_to.substring(0, 16)
      };
    } else {
      this.resetForm();
    }
    this.showModal = true;
  }

  resetForm() {
    this.voucherForm = {
      code: '',
      description: '',
      discount_type: 0,
      discount_value: 0,
      max_usage: 100,
      min_order_amount: 0,
      valid_from: new Date().toISOString().substring(0, 16),
      valid_to: '',
      is_active: true
    };
  }

  saveVoucher() {
    const request = this.editingVoucher 
      ? this.adminService.updateVoucher(this.editingVoucher.voucher_id, this.voucherForm)
      : this.adminService.createVoucher(this.voucherForm);

    request.subscribe({
      next: () => {
        this.loadVouchers();
        this.showModal = false;
      },
      error: (err) => alert(err.error?.detail || 'Lỗi lưu voucher')
    });
  }

  deleteVoucher(id: number) {
    if (confirm('Xác nhận xóa voucher này?')) {
      this.adminService.deleteVoucher(id).subscribe(() => this.loadVouchers());
    }
  }

  switchTab(tab: 'active' | 'trash') {
    this.activeTab = tab;
    this.skip = 0;
    this.applyFilterAndTab();
  }
}