class ReportGenerator:
    def generate_report(self, scan_results, target):
        start_time = scan_results['stats']['start_time']
        end_time = scan_results['stats']['end_time']
        duration = scan_results['stats']['duration']
        
        report_html = f"""
        <!-- ... existing HTML ... -->
        <div class="scan-summary">
            <h2 class="section-title">Scan Summary</h2>
            <div class="summary-grid">
                <div class="stat-card">
                    <div class="stat-number">1</div>
                    <div class="stat-label">URLs Scanned</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(scan_results['findings'])}</div>
                    <div class="stat-label">Issues Found</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{duration}</div>
                    <div class="stat-label">Scan Duration</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">16</div>
                    <div class="stat-label">Tests Performed</div>
                </div>
            </div>
        </div>
        <!-- ... rest of the HTML ... -->
        """
        return report_html 