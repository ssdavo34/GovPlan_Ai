// GovPlan_AI Frontend JavaScript

const API_BASE_URL = 'http://localhost:8000/api/v1';

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    console.log('GovPlan_AI Dashboard Loading...');

    // 통계 로드
    loadStatistics();

    // 최근 공고 로드
    loadRecentProjects();

    // 카테고리별 차트 로드
    loadCategoryChart();

    // 시스템 상태 체크
    checkSystemHealth();
});

// 통계 로드
async function loadStatistics() {
    try {
        const response = await fetch(`${API_BASE_URL}/projects/stats/summary`);
        const data = await response.json();

        document.getElementById('total-projects').textContent = data.total.total || 0;
        document.getElementById('active-projects').textContent = data.total.active || 0;

        // 매칭 및 사업계획서는 임의 값 (실제로는 사용자별 데이터 필요)
        document.getElementById('my-matches').textContent = '12';
        document.getElementById('my-proposals').textContent = '3';

    } catch (error) {
        console.error('통계 로드 실패:', error);
        document.getElementById('total-projects').textContent = 'N/A';
        document.getElementById('active-projects').textContent = 'N/A';
    }
}

// 최근 공고 로드
async function loadRecentProjects() {
    const container = document.getElementById('recent-projects');

    try {
        const response = await fetch(`${API_BASE_URL}/projects?limit=10&status=active`);
        const data = await response.json();

        if (!data.items || data.items.length === 0) {
            container.innerHTML = '<p class="text-muted text-center">등록된 공고가 없습니다.</p>';
            return;
        }

        container.innerHTML = '';

        data.items.forEach((project, index) => {
            const projectEl = createProjectElement(project, index);
            container.appendChild(projectEl);
        });

    } catch (error) {
        console.error('공고 로드 실패:', error);
        container.innerHTML = '<p class="text-danger text-center">공고를 불러오는데 실패했습니다.</p>';
    }
}

// 공고 요소 생성
function createProjectElement(project, index) {
    const div = document.createElement('div');
    div.className = 'list-group-item project-item';

    const endDate = project.application_end_date ? new Date(project.application_end_date).toLocaleDateString('ko-KR') : 'N/A';

    div.innerHTML = `
        <div class="d-flex w-100 justify-content-between align-items-start">
            <div>
                <h6 class="mb-1">${index + 1}. ${project.project_name || 'N/A'}</h6>
                <p class="mb-1 text-muted small">
                    <i class="bi bi-building"></i> ${project.agency || 'N/A'} |
                    <i class="bi bi-calendar"></i> 마감: ${endDate}
                </p>
                ${project.support_amount ? `<p class="mb-0 small"><i class="bi bi-cash"></i> ${project.support_amount}</p>` : ''}
            </div>
            <div class="text-end">
                <span class="badge bg-primary">${project.support_type || '일반'}</span>
                ${project.project_url ? `<br><a href="${project.project_url}" target="_blank" class="btn btn-sm btn-outline-primary mt-2">상세보기</a>` : ''}
            </div>
        </div>
    `;

    return div;
}

// 카테고리별 차트 로드
async function loadCategoryChart() {
    const container = document.getElementById('category-chart');

    try {
        const response = await fetch(`${API_BASE_URL}/projects/stats/summary`);
        const data = await response.json();

        if (!data.by_category || data.by_category.length === 0) {
            container.innerHTML = '<p class="text-muted text-center col-12">카테고리 데이터가 없습니다.</p>';
            return;
        }

        container.innerHTML = '';

        const maxCount = Math.max(...data.by_category.map(cat => cat.count));

        data.by_category.forEach(category => {
            const col = document.createElement('div');
            col.className = 'col-md-6 mb-3';

            const percentage = (category.count / maxCount * 100).toFixed(0);

            col.innerHTML = `
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <span>${category.support_type || 'N/A'}</span>
                    <span class="badge bg-primary">${category.count}건</span>
                </div>
                <div class="progress" style="height: 25px;">
                    <div class="progress-bar" role="progressbar" style="width: ${percentage}%"
                         aria-valuenow="${percentage}" aria-valuemin="0" aria-valuemax="100">
                        ${percentage}%
                    </div>
                </div>
            `;

            container.appendChild(col);
        });

    } catch (error) {
        console.error('차트 로드 실패:', error);
        container.innerHTML = '<p class="text-danger text-center col-12">차트를 불러오는데 실패했습니다.</p>';
    }
}

// 시스템 헬스 체크
async function checkSystemHealth() {
    try {
        const response = await fetch('http://localhost:8000/health');
        const data = await response.json();

        if (data.status === 'healthy') {
            document.getElementById('api-status').textContent = '정상';
            document.getElementById('api-status').className = 'badge bg-success';
        } else {
            document.getElementById('api-status').textContent = '오류';
            document.getElementById('api-status').className = 'badge bg-danger';
        }
    } catch (error) {
        console.error('헬스 체크 실패:', error);
        document.getElementById('api-status').textContent = '연결 실패';
        document.getElementById('api-status').className = 'badge bg-danger';
    }
}

// 퀵 액션 함수들
function searchProjects() {
    window.location.href = '/projects';
}

function calculateMatching() {
    alert('매칭 계산 기능은 로그인 후 사용 가능합니다.');
}

function generateProposal() {
    alert('사업계획서 생성 기능은 로그인 후 사용 가능합니다.');
}

async function runCrawler() {
    if (confirm('크롤링을 시작하시겠습니까? 수 분이 소요될 수 있습니다.')) {
        try {
            const response = await fetch(`${API_BASE_URL}/projects/refresh`, {
                method: 'POST'
            });
            const data = await response.json();

            alert(data.message);

            // 3초 후 새로고침
            setTimeout(() => {
                location.reload();
            }, 3000);
        } catch (error) {
            console.error('크롤링 실행 실패:', error);
            alert('크롤링 실행 중 오류가 발생했습니다.');
        }
    }
}

// 유틸리티 함수
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR');
}

function formatNumber(num) {
    if (!num) return '0';
    return num.toLocaleString('ko-KR');
}

// 자동 새로고침 (5분마다)
setInterval(() => {
    loadStatistics();
    loadRecentProjects();
    checkSystemHealth();
}, 5 * 60 * 1000);
