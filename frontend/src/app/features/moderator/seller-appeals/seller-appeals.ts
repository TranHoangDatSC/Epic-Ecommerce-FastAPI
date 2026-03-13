import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ModeratorService } from '../../../shared/services/moderator.service';

interface SellerAppeal {
  appeal_id: number;
  seller: {
    user_id: number;
    full_name: string;
    email: string;
  };
  product?: {
    product_id: number;
    title: string;
  };
  appeal_type: 'product_rejection' | 'account_suspension' | 'violation_penalty';
  appeal_reason: string;
  appeal_details: string;
  status: 'pending' | 'under_review' | 'approved' | 'rejected';
  submitted_at: string;
  reviewed_at?: string;
  reviewer_notes?: string;
}

@Component({
  selector: 'app-seller-appeals',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './seller-appeals.html',
  styleUrl: './seller-appeals.scss'
})
export class SellerAppealsComponent implements OnInit {
  appeals: SellerAppeal[] = [];
  filteredAppeals: SellerAppeal[] = [];
  searchTerm: string = '';
  selectedStatus: string = '';
  selectedAppealType: string = '';
  selectedAppeal: SellerAppeal | null = null;
  showReviewModal: boolean = false;
  reviewDecision: 'approve' | 'reject' = 'approve';
  reviewerNotes: string = '';
  processingAppeal: number | null = null;

  statuses = [
    { value: '', label: 'Tất cả trạng thái' },
    { value: 'pending', label: 'Chờ xử lý' },
    { value: 'under_review', label: 'Đang xem xét' },
    { value: 'approved', label: 'Đã chấp nhận' },
    { value: 'rejected', label: 'Đã từ chối' }
  ];

  appealTypes = [
    { value: '', label: 'Tất cả loại' },
    { value: 'product_rejection', label: 'Từ chối sản phẩm' },
    { value: 'account_suspension', label: 'Khóa tài khoản' },
    { value: 'violation_penalty', label: 'Phạt vi phạm' }
  ];

  constructor(private moderatorService: ModeratorService) {}

  ngOnInit() {
    this.loadSellerAppeals();
  }

  loadSellerAppeals() {
    this.moderatorService.getSellerAppeals().subscribe({
      next: (appeals) => {
        this.appeals = appeals;
        this.applyFilters();
      },
      error: (error) => {
        console.error('Error loading seller appeals:', error);
      }
    });
  }

  applyFilters() {
    let filtered = this.appeals;

    // Search filter
    if (this.searchTerm) {
      filtered = filtered.filter(appeal =>
        appeal.seller.full_name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        appeal.seller.email.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        (appeal.product && appeal.product.title.toLowerCase().includes(this.searchTerm.toLowerCase()))
      );
    }

    // Status filter
    if (this.selectedStatus) {
      filtered = filtered.filter(appeal => appeal.status === this.selectedStatus);
    }

    // Appeal type filter
    if (this.selectedAppealType) {
      filtered = filtered.filter(appeal => appeal.appeal_type === this.selectedAppealType);
    }

    this.filteredAppeals = filtered;
  }

  getStatusBadge(status: string): { text: string, class: string } {
    switch (status) {
      case 'pending': return { text: 'Chờ xử lý', class: 'bg-warning' };
      case 'under_review': return { text: 'Đang xem xét', class: 'bg-info' };
      case 'approved': return { text: 'Đã chấp nhận', class: 'bg-success' };
      case 'rejected': return { text: 'Đã từ chối', class: 'bg-danger' };
      default: return { text: 'Không xác định', class: 'bg-secondary' };
    }
  }

  getAppealTypeLabel(type: string): string {
    const appealType = this.appealTypes.find(a => a.value === type);
    return appealType ? appealType.label : type;
  }

  openReviewModal(appeal: SellerAppeal) {
    this.selectedAppeal = appeal;
    this.reviewDecision = 'approve';
    this.reviewerNotes = '';
    this.showReviewModal = true;
  }

  closeReviewModal() {
    this.showReviewModal = false;
    this.selectedAppeal = null;
    this.reviewDecision = 'approve';
    this.reviewerNotes = '';
  }

  submitReview() {
    if (!this.selectedAppeal) return;

    this.processingAppeal = this.selectedAppeal.appeal_id;

    this.moderatorService.reviewSellerAppeal(
      this.selectedAppeal.appeal_id,
      this.reviewDecision,
      this.reviewerNotes
    ).subscribe({
      next: () => {
        // Update the appeal status locally
        const index = this.appeals.findIndex(a => a.appeal_id === this.selectedAppeal!.appeal_id);
        if (index !== -1) {
          this.appeals[index].status = this.reviewDecision === 'approve' ? 'approved' : 'rejected';
          this.appeals[index].reviewed_at = new Date().toISOString();
          this.appeals[index].reviewer_notes = this.reviewerNotes;
        }
        this.applyFilters();
        this.closeReviewModal();
        this.processingAppeal = null;
      },
      error: (error) => {
        console.error('Error reviewing appeal:', error);
        this.processingAppeal = null;
      }
    });
  }

  clearFilters() {
    this.searchTerm = '';
    this.selectedStatus = '';
    this.selectedAppealType = '';
    this.applyFilters();
  }
}