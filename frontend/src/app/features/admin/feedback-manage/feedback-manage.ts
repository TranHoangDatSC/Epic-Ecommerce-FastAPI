import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AdminService } from '../../../shared/services/admin.service';

@Component({
  selector: 'app-feedback-manage',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './feedback-manage.html',
  styleUrl: './feedback-manage.scss'
})
export class FeedbackManageComponent implements OnInit {
  feedbacks: any[] = [];
  isLoading = false;
  skip = 0;
  limit = 20;

  constructor(
    private adminService: AdminService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadFeedbacks();
  }

  loadFeedbacks() {
    this.isLoading = true;
    this.adminService.getFeedbacks(this.skip, this.limit).subscribe({
      next: (data) => {
        this.feedbacks = data;
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error loading feedbacks:', err);
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  updateStatus(feedbackId: number, status: number) {
    this.adminService.updateFeedbackStatus(feedbackId, status).subscribe(() => this.loadFeedbacks());
  }

  getStatusClass(status: number) {
    switch (status) {
      case 0: return 'bg-amber-500/10 text-amber-500 border-amber-500/20'; // Pending
      case 1: return 'bg-blue-500/10 text-blue-500 border-blue-500/20'; // Reviewed
      case 2: return 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20'; // Resolved
      default: return 'bg-gray-500/10 text-gray-500 border-gray-500/20';
    }
  }

  getStatusLabel(status: number) {
    switch (status) {
      case 0: return 'Untouched';
      case 1: return 'Archived';
      case 2: return 'Cleared';
      default: return 'Unknown';
    }
  }
}
