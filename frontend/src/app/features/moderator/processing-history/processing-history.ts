import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ModeratorService } from '../../../shared/services/moderator.service';

interface ProcessingHistory {
  id: number;
  action_type: 'approve_product' | 'reject_product' | 'violation_report' | 'unlock_account' | 'ban_user';
  target_type: 'product' | 'user' | 'review';
  target_id: number;
  target_title: string;
  action_details: string;
  created_at: string;
  moderator: {
    full_name: string;
  };
}

@Component({
  selector: 'app-processing-history',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './processing-history.html',
  styleUrl: './processing-history.scss'
})
export class ProcessingHistoryComponent implements OnInit {
  history: ProcessingHistory[] = [];
  filteredHistory: ProcessingHistory[] = [];
  searchTerm: string = '';
  selectedActionType: string = '';
  selectedDateRange: string = '';
  currentPage: number = 1;
  itemsPerPage: number = 20;
  totalPages: number = 1;

  actionTypes = [
    { value: '', label: 'Tất cả hành động' },
    { value: 'approve_product', label: 'Duyệt sản phẩm' },
    { value: 'reject_product', label: 'Từ chối sản phẩm' },
    { value: 'violation_report', label: 'Xử lý vi phạm' },
    { value: 'unlock_account', label: 'Mở khóa tài khoản' },
    { value: 'ban_user', label: 'Khóa tài khoản' }
  ];

  dateRanges = [
    { value: '', label: 'Tất cả thời gian' },
    { value: 'today', label: 'Hôm nay' },
    { value: 'week', label: 'Tuần này' },
    { value: 'month', label: 'Tháng này' }
  ];

  constructor(private moderatorService: ModeratorService) {}

  ngOnInit() {
    this.loadProcessingHistory();
  }

  loadProcessingHistory() {
    this.moderatorService.getProcessingHistory().subscribe({
      next: (history) => {
        this.history = history;
        this.applyFilters();
      },
      error: (error) => {
        console.error('Error loading processing history:', error);
      }
    });
  }

  applyFilters() {
    let filtered = this.history;

    // Search filter
    if (this.searchTerm) {
      filtered = filtered.filter(item =>
        item.target_title.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        item.moderator.full_name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        item.action_details.toLowerCase().includes(this.searchTerm.toLowerCase())
      );
    }

    // Action type filter
    if (this.selectedActionType) {
      filtered = filtered.filter(item => item.action_type === this.selectedActionType);
    }

    // Date range filter
    if (this.selectedDateRange) {
      const now = new Date();
      let startDate: Date;

      switch (this.selectedDateRange) {
        case 'today':
          startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
          break;
        case 'week':
          startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
          break;
        case 'month':
          startDate = new Date(now.getFullYear(), now.getMonth(), 1);
          break;
        default:
          startDate = new Date(0);
      }

      filtered = filtered.filter(item => new Date(item.created_at) >= startDate);
    }

    this.filteredHistory = filtered;
    this.totalPages = Math.ceil(this.filteredHistory.length / this.itemsPerPage);
    this.currentPage = 1;
  }

  get paginatedHistory(): ProcessingHistory[] {
    const startIndex = (this.currentPage - 1) * this.itemsPerPage;
    const endIndex = startIndex + this.itemsPerPage;
    return this.filteredHistory.slice(startIndex, endIndex);
  }

  getActionTypeLabel(actionType: string): string {
    const action = this.actionTypes.find(a => a.value === actionType);
    return action ? action.label : actionType;
  }

  getActionIcon(actionType: string): string {
    switch (actionType) {
      case 'approve_product': return 'fas fa-check-circle';
      case 'reject_product': return 'fas fa-times-circle';
      case 'violation_report': return 'fas fa-exclamation-triangle';
      case 'unlock_account': return 'fas fa-unlock';
      case 'ban_user': return 'fas fa-ban';
      default: return 'fas fa-cog';
    }
  }

  getActionColor(actionType: string): string {
    switch (actionType) {
      case 'approve_product': return 'text-success';
      case 'reject_product': return 'text-danger';
      case 'violation_report': return 'text-warning';
      case 'unlock_account': return 'text-info';
      case 'ban_user': return 'text-danger';
      default: return 'text-secondary';
    }
  }

  clearFilters() {
    this.searchTerm = '';
    this.selectedActionType = '';
    this.selectedDateRange = '';
    this.applyFilters();
  }

  previousPage() {
    if (this.currentPage > 1) {
      this.currentPage--;
    }
  }

  nextPage() {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
    }
  }

  goToPage(page: number) {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
    }
  }
}