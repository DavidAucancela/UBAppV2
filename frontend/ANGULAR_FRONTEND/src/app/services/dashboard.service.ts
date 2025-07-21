import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface DashboardStats {
  total_envios: number;
  total_productos: number;
  total_usuarios: number;
  total_compradores: number;
  valor_total_envios: number;
  peso_total_envios: number;
  envios_mes_actual: number;
  productos_mes_actual: number;
  valor_mes_actual: number;
  cambio_envios_mes: number;
  cambio_productos_mes: number;
  cambio_valor_mes: number;
  envios_por_estado: { [key: string]: number };
  productos_por_categoria: { [key: string]: number };
  actividad_reciente: UserActivity[];
}

export interface UserActivity {
  id: number;
  user_name: string;
  action_display: string;
  description: string;
  created_at: string;
}

export interface ChartData {
  labels: string[];
  datasets: ChartDataset[];
}

export interface ChartDataset {
  label: string;
  data: number[];
  backgroundColor: string;
  borderColor: string;
}

export interface MetricsSummary {
  period: string;
  envios_data: ChartData;
  productos_data: ChartData;
  usuarios_data: ChartData;
  financial_data: ChartData;
}

export interface Report {
  id?: number;
  name: string;
  report_type: string;
  report_type_display?: string;
  description: string;
  parameters: any;
  status: string;
  status_display?: string;
  result_data: any;
  file_path?: string;
  date_from?: string;
  date_to?: string;
  created_at?: string;
  updated_at?: string;
  completed_at?: string;
  requested_by?: number;
  requested_by_info?: any;
}

export interface DashboardMetric {
  id: number;
  metric_type: string;
  metric_type_display: string;
  period_type: string;
  period_type_display: string;
  date: string;
  value: number;
  count: number;
  metadata: any;
  created_at: string;
  updated_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  private baseUrl = `${environment.apiUrl}/dashboard`;

  constructor(private http: HttpClient) { }

  // Dashboard Stats
  getDashboardStats(): Observable<DashboardStats> {
    return this.http.get<DashboardStats>(`${this.baseUrl}/stats/`);
  }

  // Metrics Summary
  getMetricsSummary(period: string = 'monthly'): Observable<MetricsSummary> {
    const params = new HttpParams().set('period', period);
    return this.http.get<MetricsSummary>(`${this.baseUrl}/metrics-summary/`, { params });
  }

  // Reports
  getReports(filters?: any): Observable<any> {
    let params = new HttpParams();
    if (filters) {
      Object.keys(filters).forEach(key => {
        if (filters[key]) {
          params = params.set(key, filters[key]);
        }
      });
    }
    return this.http.get<any>(`${this.baseUrl}/reports/`, { params });
  }

  getReport(id: number): Observable<Report> {
    return this.http.get<Report>(`${this.baseUrl}/reports/${id}/`);
  }

  createReport(report: Partial<Report>): Observable<Report> {
    return this.http.post<Report>(`${this.baseUrl}/reports/`, report);
  }

  generateReport(id: number): Observable<Report> {
    return this.http.post<Report>(`${this.baseUrl}/reports/${id}/generate/`, {});
  }

  updateReport(id: number, report: Partial<Report>): Observable<Report> {
    return this.http.put<Report>(`${this.baseUrl}/reports/${id}/`, report);
  }

  deleteReport(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/reports/${id}/`);
  }

  // Metrics
  getMetrics(filters?: any): Observable<any> {
    let params = new HttpParams();
    if (filters) {
      Object.keys(filters).forEach(key => {
        if (filters[key]) {
          params = params.set(key, filters[key]);
        }
      });
    }
    return this.http.get<any>(`${this.baseUrl}/metrics/`, { params });
  }

  getMetric(id: number): Observable<DashboardMetric> {
    return this.http.get<DashboardMetric>(`${this.baseUrl}/metrics/${id}/`);
  }

  createMetric(metric: Partial<DashboardMetric>): Observable<DashboardMetric> {
    return this.http.post<DashboardMetric>(`${this.baseUrl}/metrics/`, metric);
  }

  updateMetric(id: number, metric: Partial<DashboardMetric>): Observable<DashboardMetric> {
    return this.http.put<DashboardMetric>(`${this.baseUrl}/metrics/${id}/`, metric);
  }

  deleteMetric(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/metrics/${id}/`);
  }

  // User Activities
  getUserActivities(filters?: any): Observable<any> {
    let params = new HttpParams();
    if (filters) {
      Object.keys(filters).forEach(key => {
        if (filters[key]) {
          params = params.set(key, filters[key]);
        }
      });
    }
    return this.http.get<any>(`${this.baseUrl}/activities/`, { params });
  }

  getUserActivity(id: number): Observable<UserActivity> {
    return this.http.get<UserActivity>(`${this.baseUrl}/activities/${id}/`);
  }

  // Utility methods for chart colors
  getChartColors(count: number): string[] {
    const colors = [
      'rgba(54, 162, 235, 0.6)',
      'rgba(255, 99, 132, 0.6)',
      'rgba(75, 192, 192, 0.6)',
      'rgba(153, 102, 255, 0.6)',
      'rgba(255, 159, 64, 0.6)',
      'rgba(255, 206, 86, 0.6)',
      'rgba(231, 76, 60, 0.6)',
      'rgba(46, 204, 113, 0.6)',
      'rgba(155, 89, 182, 0.6)',
      'rgba(52, 152, 219, 0.6)'
    ];
    
    const result = [];
    for (let i = 0; i < count; i++) {
      result.push(colors[i % colors.length]);
    }
    return result;
  }

  getBorderColors(count: number): string[] {
    const colors = [
      'rgba(54, 162, 235, 1)',
      'rgba(255, 99, 132, 1)',
      'rgba(75, 192, 192, 1)',
      'rgba(153, 102, 255, 1)',
      'rgba(255, 159, 64, 1)',
      'rgba(255, 206, 86, 1)',
      'rgba(231, 76, 60, 1)',
      'rgba(46, 204, 113, 1)',
      'rgba(155, 89, 182, 1)',
      'rgba(52, 152, 219, 1)'
    ];
    
    const result = [];
    for (let i = 0; i < count; i++) {
      result.push(colors[i % colors.length]);
    }
    return result;
  }

  // Format numbers for display
  formatNumber(value: number): string {
    if (value >= 1000000) {
      return (value / 1000000).toFixed(1) + 'M';
    } else if (value >= 1000) {
      return (value / 1000).toFixed(1) + 'K';
    }
    return value.toString();
  }

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  }

  formatWeight(value: number): string {
    return `${value.toFixed(2)} kg`;
  }

  formatPercentage(value: number): string {
    return `${value.toFixed(1)}%`;
  }
}