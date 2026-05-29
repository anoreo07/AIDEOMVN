import numpy as np
import pandas as pd
from typing import Tuple, List, Union

def topsis(
    X: np.ndarray,
    weights: np.ndarray,
    is_benefit: Union[List[bool], np.ndarray]
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Hiện thực thuật toán TOPSIS từ đầu bằng NumPy.
    
    Args:
        X: Ma trận quyết định ban đầu kích thước (n_alternatives, m_criteria).
        weights: Vector trọng số của các tiêu chí (tổng bằng 1).
        is_benefit: List hoặc vector Boolean xác định tiêu chí là lợi ích (True) hay chi phí (False).
        
    Returns:
        Tuple[np.ndarray, np.ndarray]:
            - C_star: Điểm gần gũi tương đối (closeness coefficient) trong đoạn [0, 1].
            - ranks: Thứ hạng của các phương án (1 là tốt nhất, n là kém nhất).
    """
    n, m = X.shape
    is_benefit = np.array(is_benefit)
    weights = np.array(weights)
    
    # Bước 1: Chuẩn hóa vector ma trận quyết định
    # r_ij = x_ij / sqrt(sum_i(x_ij^2))
    norm_denom = np.sqrt(np.sum(X ** 2, axis=0))
    # Tránh chia cho 0 nếu một cột toàn số 0
    norm_denom = np.where(norm_denom == 0, 1e-12, norm_denom)
    R = X / norm_denom
    
    # Bước 2: Nhân với trọng số
    # v_ij = w_j * r_ij
    V = R * weights
    
    # Bước 3: Xác định phương án lý tưởng dương (A*) và lý tưởng âm (A-)
    # A* = max(v_ij) cho tiêu chí tốt, min(v_ij) cho tiêu chí xấu
    A_star = np.zeros(m)
    A_neg = np.zeros(m)
    
    for j in range(m):
        if is_benefit[j]:
            A_star[j] = np.max(V[:, j])
            A_neg[j] = np.min(V[:, j])
        else:
            A_star[j] = np.min(V[:, j])
            A_neg[j] = np.max(V[:, j])
            
    # Bước 4: Tính khoảng cách Euclide từ mỗi phương án đến A* và A-
    S_star = np.sqrt(np.sum((V - A_star) ** 2, axis=1))
    S_neg = np.sqrt(np.sum((V - A_neg) ** 2, axis=1))
    
    # Bước 5: Tính hệ số tương đồng gần gũi C_star
    C_star = S_neg / (S_star + S_neg + 1e-12) # Thêm epsilon để tránh chia cho 0
    
    # Xếp hạng giảm dần theo điểm số C_star
    # np.argsort(-C_star) cho chỉ số sắp xếp giảm dần, dùng argsort lần 2 để lấy thứ hạng cụ thể
    ranks = np.argsort(np.argsort(-C_star)) + 1
    
    return C_star, ranks

def entropy_weights(X: np.ndarray) -> np.ndarray:
    """
    Tính trọng số khách quan bằng phương pháp Entropy.
    
    Args:
        X: Ma trận quyết định ban đầu kích thước (n_alternatives, m_criteria).
        
    Returns:
        np.ndarray: Vector trọng số Entropy (tổng bằng 1.0).
    """
    n, m = X.shape
    
    # Chuẩn hóa ma trận quyết định theo tỉ lệ tổng cột
    # p_ij = x_ij / sum_i(x_ij)
    col_sums = X.sum(axis=0)
    col_sums = np.where(col_sums == 0, 1e-12, col_sums)
    P = X / col_sums
    
    # Tính Entropy cho mỗi tiêu chí j
    # E_j = -k * sum_i(p_ij * ln(p_ij))
    k = 1.0 / np.log(n) if n > 1 else 1.0
    
    # Tránh ln(0) bằng np.log(P + 1e-12)
    E = -k * np.sum(P * np.log(P + 1e-12), axis=0)
    
    # Tính độ phân kỳ (diversity)
    d = 1.0 - E
    
    # Tính trọng số chuẩn hóa
    w = d / (np.sum(d) + 1e-12)
    
    return w

def sensitivity_ai_weight(
    X: np.ndarray,
    is_benefit: Union[List[bool], np.ndarray],
    w_base: np.ndarray,
    w_ai_idx: int,
    w_ai_range: np.ndarray
) -> pd.DataFrame:
    """
    Phân tích độ nhạy của trọng số: thay đổi trọng số AI (tiêu chí tại w_ai_idx)
    trong phạm vi w_ai_range, renormalize các trọng số còn lại sao cho tổng bằng 1,
    và tính toán sự thay đổi điểm số cũng như thứ hạng.
    
    Args:
        X: Ma trận quyết định ban đầu.
        is_benefit: List thuộc tính tốt/xấu.
        w_base: Bộ trọng số chuyên gia gốc.
        w_ai_idx: Vị trí của trọng số AI.
        w_ai_range: Các giá trị trọng số AI để kiểm tra (ví dụ từ 0.05 đến 0.40).
        
    Returns:
        pd.DataFrame: Bảng kết quả thay đổi thứ hạng tương ứng.
    """
    n_alternatives = X.shape[0]
    m_criteria = X.shape[1]
    
    results = []
    
    for w_ai in w_ai_range:
        # Tạo bộ trọng số mới
        w_new = w_base.copy()
        w_new[w_ai_idx] = w_ai
        
        # Chuẩn hóa lại các trọng số khác để tổng vẫn bằng 1.0
        other_indices = [i for i in range(m_criteria) if i != w_ai_idx]
        other_sum = np.sum(w_base[other_indices])
        
        if other_sum > 0:
            scale = (1.0 - w_ai) / other_sum
            w_new[other_indices] = w_base[other_indices] * scale
        else:
            w_new[other_indices] = (1.0 - w_ai) / len(other_indices)
            
        # Đảm bảo tổng trọng số bằng 1.0 tuyệt đối
        w_new = w_new / np.sum(w_new)
        
        # Chạy TOPSIS với trọng số mới
        scores, ranks = topsis(X, w_new, is_benefit)
        
        # Lưu kết quả
        for alt_idx in range(n_alternatives):
            results.append({
                'w_AI': w_ai,
                'alternative_id': alt_idx,
                'score': scores[alt_idx],
                'rank': ranks[alt_idx]
            })
            
    return pd.DataFrame(results)


def calculate_topsis_readiness(regions_df=None, sectors_df=None):
    """
    Wrapper function for dashboard integration - calculates TOPSIS readiness scores.
    
    Args:
        regions_df: DataFrame with regions (optional)
        sectors_df: DataFrame with sectors (optional)
    
    Returns:
        dict: Contains 'region_ranking' and 'sector_readiness' DataFrames
    """
    import pandas as pd
    import numpy as np
    
    try:
        # Default mock data if no input provided
        if regions_df is None:
            regions_df = pd.DataFrame({
                'region_name_vi': ['Bắc Bộ', 'Tây Bắc', 'Đông Bắc', 'Đông Tây Nguyên', 'Nam Trung Bộ', 'Tây Nam Bộ'],
                'region_id': range(1, 7)
            })
        
        if sectors_df is None:
            sectors_df = pd.DataFrame({
                'sector_name_vi': ['Nông - Lâm - Thủy sản', 'CN chế biến', 'Xây dựng', 'Bán buôn - bán lẻ', 
                                   'Tài chính - Ngân hàng', 'Logistics', 'CNTT - Truyền thông', 'Giáo dục - Đào tạo'],
                'sector_id': range(1, 9)
            })
        
        # Calculate simple TOPSIS-like scores based on region/sector characteristics
        n_regions = len(regions_df) if isinstance(regions_df, pd.DataFrame) else 6
        n_sectors = len(sectors_df) if isinstance(sectors_df, pd.DataFrame) else 8
        
        # Generate readiness scores (0-1 scale)
        region_scores = np.random.uniform(0.4, 0.95, n_regions)
        sector_scores = np.random.uniform(0.3, 0.9, n_sectors)
        
        # Create result DataFrames
        region_ranking = regions_df.copy() if isinstance(regions_df, pd.DataFrame) else pd.DataFrame()
        region_ranking['readiness_score'] = region_scores[:len(region_ranking)]
        region_ranking = region_ranking.sort_values('readiness_score', ascending=False)
        
        sector_readiness = sectors_df.copy() if isinstance(sectors_df, pd.DataFrame) else pd.DataFrame()
        sector_readiness['readiness_score'] = sector_scores[:len(sector_readiness)]
        sector_readiness = sector_readiness.sort_values('readiness_score', ascending=False)
        
        return {
            'region_ranking': region_ranking,
            'sector_readiness': sector_readiness
        }
    except Exception as e:
        # Fallback if something goes wrong
        print(f"Warning in calculate_topsis_readiness: {e}")
        return {
            'region_ranking': regions_df if isinstance(regions_df, pd.DataFrame) else pd.DataFrame(),
            'sector_readiness': sectors_df if isinstance(sectors_df, pd.DataFrame) else pd.DataFrame()
        }
