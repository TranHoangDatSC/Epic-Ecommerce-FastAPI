import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { ModeratorService } from '../../../shared/services/moderator.service';

interface Review {
  review_id: number;
  product_id: number;
  rating: number;
  title?: string;
  content?: string;
  created_at: string;
  buyer_id: number;
  reviewer?: {
    user_id: number;
    full_name: string;
  };
}

@Component({
  selector: 'app-violation-report',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './violation-report.html',
  styleUrl: './violation-report.scss'
})
export class ViolationReportComponent implements OnInit {
  violationReviews: Review[] = [];
  processingReview: number | null = null;
  showViolationModal: boolean = false;
  selectedReview: Review | null = null;

  // Ban options
  shouldBanUser: boolean = false;
  banReason: string = 'fraud';
  banDuration: string = '7';
  banNote: string = '';

  // Sensitive words for highlighting
  private sensitiveWords = [
    'lừa đảo', 'lừa', 'gian lận', 'fake', 'giả', 'hàng kém chất lượng',
    'hàng giả', 'hàng nhái', 'quá hạn', 'hỏng', 'không như mô tả',
    'thanh toán trước', 'cọc trước', 'chuyển khoản trước'
  ];

  constructor(private moderatorService: ModeratorService) {}

  ngOnInit() {
    this.loadViolationReviews();
  }

  loadViolationReviews() {
    this.moderatorService.getViolationReviews().subscribe({
      next: (reviews) => {
        this.violationReviews = reviews;
      },
      error: (error) => {
        console.error('Error loading violation reviews:', error);
        // TODO: Show error message to user
      }
    });
  }

  isHighlightedReview(review: Review): boolean {
    return review.rating === 1 && this.containsSensitiveWords(review.content || '');
  }

  containsSensitiveWords(text: string): boolean {
    const lowerText = text.toLowerCase();
    return this.sensitiveWords.some(word => lowerText.includes(word.toLowerCase()));
  }

  getSensitiveWords(text: string): string[] {
    if (!text) return [];
    const lowerText = text.toLowerCase();
    return this.sensitiveWords.filter(word => lowerText.includes(word.toLowerCase()));
  }

  viewReviewDetails(review: Review) {
    // TODO: Navigate to detailed review view or open modal
    console.log('View review details:', review);
  }

  openViolationModal(review: Review) {
    this.selectedReview = review;
    this.showViolationModal = true;
    this.shouldBanUser = false;
    this.banReason = 'fraud';
    this.banDuration = '7';
    this.banNote = '';
  }

  closeViolationModal() {
    this.showViolationModal = false;
    this.selectedReview = null;
  }

  confirmViolation() {
    if (!this.selectedReview || this.processingReview) return;

    this.processingReview = this.selectedReview.review_id;

    // Handle violation confirmation
    this.moderatorService.handleViolation(this.selectedReview.review_id).subscribe({
      next: (result) => {
        console.log('Violation handled:', result);

        // If user should be banned
        if (this.shouldBanUser) {
          this.banUser();
        } else {
          this.finishProcessing();
        }
      },
      error: (error) => {
        console.error('Error handling violation:', error);
        this.processingReview = null;
        // TODO: Show error message
      }
    });
  }

  private banUser() {
    if (!this.selectedReview) return;

    // TODO: Get user ID from review - this might need API changes
    const userId = 1; // Placeholder - need to get actual user ID

    this.moderatorService.banUser(userId, this.banReason).subscribe({
      next: (result) => {
        console.log('User banned:', result);
        this.finishProcessing();
      },
      error: (error) => {
        console.error('Error banning user:', error);
        this.finishProcessing();
        // TODO: Show error message
      }
    });
  }

  private finishProcessing() {
    this.processingReview = null;
    this.closeViolationModal();
    this.loadViolationReviews(); // Refresh the list
  }

  getStarDisplay(rating: number): string {
    let stars = '';
    for (let i = 1; i <= 5; i++) {
      stars += i <= rating ? '★' : '☆';
    }
    return stars;
  }
}