import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ModeratorService } from '../../../shared/services/moderator.service';

interface HighPriorityItem {
  id: number;
  type: 'violation' | 'product' | 'complaint';
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  sla: string; // Service Level Agreement time
  created_at: string;
}

interface SellerReputation {
  seller_id: number;
  full_name: string;
  reputation_score: number;
  total_products: number;
  violations_count: number;
  status: 'good' | 'warning' | 'critical';
}

@Component({
  selector: 'app-moderator-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss'
})
export class ModeratorDashboardComponent implements OnInit {
  highPriorityQueue: HighPriorityItem[] = [];
  sellerReputations: SellerReputation[] = [];
  stats = {
    pendingProducts: 0,
    rejectedProducts: 0,
    archivedProducts: 0,
    violationReports: 0,
    processedToday: 0
  };

  constructor(private moderatorService: ModeratorService) {}

  ngOnInit() {
    this.loadDashboardData();
  }

  loadDashboardData() {
    // Load high priority queue
    this.loadHighPriorityQueue();
    // Load seller reputations
    this.loadSellerReputations();
    // Load stats
    this.loadStats();
  }

  loadHighPriorityQueue() {
    // Mock data for now - replace with actual API call
    this.highPriorityQueue = [
      {
        id: 1,
        type: 'violation',
        title: 'Lừa đảo tiền cọc iPhone 13',
        description: 'Người bán yêu cầu thanh toán trước, có dấu hiệu lừa đảo',
        priority: 'high',
        sla: '2 giờ',
        created_at: new Date().toISOString()
      },
      {
        id: 2,
        type: 'complaint',
        title: 'Khiếu nại sản phẩm giả',
        description: 'Khách hàng báo cáo sản phẩm không chính hãng',
        priority: 'high',
        sla: '4 giờ',
        created_at: new Date().toISOString()
      }
    ];
  }

  loadSellerReputations() {
    // Mock data - replace with API
    this.sellerReputations = [
      {
        seller_id: 1,
        full_name: 'Nguyễn Văn A',
        reputation_score: 85,
        total_products: 45,
        violations_count: 2,
        status: 'warning'
      },
      {
        seller_id: 2,
        full_name: 'Trần Thị B',
        reputation_score: 95,
        total_products: 120,
        violations_count: 0,
        status: 'good'
      }
    ];
  }

  loadStats() {
    // Mock stats - replace with API calls
    this.stats = {
      pendingProducts: 12,
      rejectedProducts: 5,
      archivedProducts: 23,
      violationReports: 8,
      processedToday: 15
    };
  }

  getPriorityClass(priority: string): string {
    switch (priority) {
      case 'high': return 'priority-high';
      case 'medium': return 'priority-medium';
      case 'low': return 'priority-low';
      default: return '';
    }
  }

  getReputationStatusClass(status: string): string {
    switch (status) {
      case 'good': return 'status-good';
      case 'warning': return 'status-warning';
      case 'critical': return 'status-critical';
      default: return '';
    }
  }

  getActionLink(item: HighPriorityItem): string {
    switch (item.type) {
      case 'violation':
        return '/moderator/violation-report';
      case 'product':
        return '/moderator/product-check';
      case 'complaint':
        return '/moderator/seller-appeals';
      default:
        return '/moderator/dashboard';
    }
  }

  getReputationStatusText(status: string): string {
    switch (status) {
      case 'good': return 'Tốt';
      case 'warning': return 'Cảnh báo';
      case 'critical': return 'Nguy hiểm';
      default: return '';
    }
  }
}