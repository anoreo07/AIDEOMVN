import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def render():
    st.title("🎯 Bài 5 — Tối ưu hóa danh mục dự án (MIP Project Selection)")
    
    st.markdown(r"""
    **Mục tiêu học tập:** Tiếp cận mô hình quy hoạch nguyên hỗn hợp (Mixed-Integer Programming - MIP). 
    Sinh viên hiểu cách đưa các điều kiện logic (Nếu-Thì, Loại trừ nhau, Ràng buộc phụ thuộc) 
    vào mô hình toán học thông qua các biến nhị phân $y_i \in \{0, 1\}$.
    """)

    tabs = st.tabs([
        "📖 Bối cảnh & Vấn đề", 
        "🔬 Mô hình MIP", 
        "🧠 Ràng buộc Logic", 
        "📊 Danh mục 15 dự án", 
        "📈 Kết quả tối ưu", 
        "💡 Thảo luận chính sách",
        "📚 Tham khảo"
    ])
    
    with tabs[0]:
        st.header("1. Bối cảnh & Vấn đề")
        st.markdown("""
        Chính phủ có danh sách 15 dự án đầu tư công nghệ tiềm năng (từ Hạ tầng dữ liệu, Trung tâm AI, 
        đến Đào tạo nhân lực bán dẫn). Mỗi dự án có chi phí đầu tư và lợi ích kỳ vọng (NPV) khác nhau.
        
        **Thách thức:** Ngân sách có hạn, và các dự án có mối quan hệ ràng buộc lẫn nhau. 
        Ví dụ: Không thể xây dựng 2 trung tâm AI cùng lúc ở một địa điểm (Loại trừ), 
        hoặc phải đầu tư vào Hệ thống Điện trước khi lắp đặt Siêu máy tính (Phụ thuộc).
        """)
        st.info("💡 **Mấu chốt:** Làm sao chọn được 'rổ' dự án có tổng NPV cao nhất mà không vi phạm các logic này?")
        
    with tabs[1]:
        st.header("2. Mô hình toán học MIP")
        st.markdown(r"""
        Gọi $y_i$ là biến nhị phân đại diện cho việc chọn dự án $i$:
        - $y_i = 1$: Nếu dự án $i$ được chọn.
        - $y_i = 0$: Nếu dự án $i$ bị loại.
        
        **Hàm mục tiêu:** Tối đa hóa tổng giá trị hiện tại ròng (NPV):
        """)
        st.latex(r"\max Z = \sum_{i=1}^{15} NPV_i \cdot y_i")
        st.markdown(r"""
        **Ràng buộc ngân sách:**
        """)
        st.latex(r"\sum_{i=1}^{15} Cost_i \cdot y_i \le Budget")

    with tabs[2]:
        st.header("3. Chuyển đổi Logic sang Toán học")
        st.markdown("Trong bài tập này, chúng ta xử lý 3 loại ràng buộc logic phổ biến:")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Loại trừ (Mutually Exclusive)")
            st.write("Dự án 1 và 2 xung đột nhau:")
            st.latex(r"y_1 + y_2 \le 1")
            
            st.subheader("Phụ thuộc (Precedence)")
            st.write("Dự án 8 chỉ được làm nếu đã chọn dự án 12:")
            st.latex(r"y_8 \le y_{12}")
        
        with col2:
            st.subheader("Bắt buộc (Mandatory)")
            st.write("Dự án 14 là an ninh quốc gia, phải chọn:")
            st.latex(r"y_{14} = 1")
            
            st.subheader("Giới hạn số lượng (Cardinality)")
            st.write("Phải chọn ít nhất 7 dự án để đảm bảo quy mô:")
            st.latex(r"\sum y_i \ge 7")

    with tabs[3]:
        st.header("4. Danh mục 15 dự án AI/Số hóa")
        
        data = {
            'ID': range(1, 16),
            'Tên dự án': [
                'Trung tâm Dữ liệu QG', 'Cloud Gov Miền Bắc', 'Mạng 5G biển đảo', 'Hệ thống e-ID',
                'Phòng Lab AI Mở', 'Trường đào tạo Bán dẫn', 'Nông nghiệp thông minh', 'AI Y tế từ xa',
                'Logistics tự hành', 'Sàn TMĐT biên giới', 'Cyber Security Hub', 'Hệ thống điện sạch',
                'Xưởng chip thử nghiệm', 'Chip An ninh QG', 'Hệ thống cảnh báo thiên tai'
            ],
            'Cost': [15000, 12000, 8000, 5000, 7000, 18000, 4000, 6000, 10000, 3000, 9000, 20000, 25000, 15000, 4500],
            'NPV': [25000, 18000, 12000, 9000, 11000, 28000, 7500, 10000, 16000, 5500, 15000, 22000, 35000, 26000, 8500]
        }
        df_p = pd.DataFrame(data)
        df_p['B/C Ratio'] = (df_p['NPV'] / df_p['Cost']).round(2)
        st.dataframe(df_p.style.highlight_max(subset=['B/C Ratio'], color='#10b981'))

    with tabs[4]:
        st.header("5. Kết quả giải bằng PuLP Solver")
        
        # Fallback if solver fails or is missing
        selected_ids = []
        
        try:
            import pulp
            
            budget = st.slider("Tổng ngân sách (Tỷ VND)", 40000, 100000, 80000, step=5000)
            
            # Solver implementation
            prob = pulp.LpProblem("Project_Selection", pulp.LpMaximize)
            y = pulp.LpVariable.dicts("y", range(1, 16), cat='Binary')
            
            # Objective
            prob += pulp.lpSum(df_p.loc[i-1, 'NPV'] * y[i] for i in range(1, 16))
            
            # Constraints
            prob += pulp.lpSum(df_p.loc[i-1, 'Cost'] * y[i] for i in range(1, 16)) <= budget
            prob += y[1] + y[2] <= 1 # Conflict
            prob += y[8] <= y[12]   # Precedence AI -> Edu
            prob += y[13] <= y[3]   # Precedence Semi -> 5G
            prob += y[14] == 1      # Mandatory
            prob += pulp.lpSum(y[i] * df_p.loc[i-1, 'Cost'] for i in [1, 2, 3, 12]) <= 35000 # Phase 1 limit
            prob += pulp.lpSum(y[i] for i in range(1, 16)) >= 7 # Min projects
            
            prob.solve(pulp.PULP_CBC_CMD(msg=0))
            
            if pulp.LpStatus[prob.status] == 'Optimal':
                selected_ids = [i for i in range(1, 16) if pulp.value(y[i]) == 1]
                total_npv = pulp.value(prob.objective)
                total_cost = sum(df_p.loc[i-1, 'Cost'] for i in selected_ids)
                
                st.success(f"Tìm thấy phương án tối ưu mang lại NPV: **{total_npv:,.0f}** tỷ VND")
                
                df_selected = df_p[df_p['ID'].isin(selected_ids)].copy()
                df_selected['Status'] = 'Selected'
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric("Số dự án chọn", len(selected_ids))
                    st.metric("Tổng chi phí", f"{total_cost:,.0f} tỷ")
                    st.write("**Danh mục được chọn:**")
                    st.write(df_selected[['Tên dự án', 'Cost']])
                    
                with col2:
                    fig = px.scatter(df_p, x='Cost', y='NPV', text='Tên dự án', size='B/C Ratio',
                                     color=df_p['ID'].isin(selected_ids).map({True:'Selected', False:'Rejected'}),
                                     color_discrete_map={'Selected':'#10b981', 'Rejected':'#ef4444'},
                                     title="Không gian dự án: Lợi ích vs Chi phí")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Không tìm thấy giải pháp tối ưu.")
        except ImportError:
            st.error("⚠️ **Xác định thiếu thư viện 'PuLP'**")
            st.markdown(r"""
            Để chạy mô hình tối ưu hóa này, vui lòng cài đặt thư viện PuLP bằng lệnh sau trong terminal:
            ```bash
            pip install pulp
            ```
            """)
            st.info("Hiển thị dữ liệu danh mục dự án thô (không tối ưu hóa):")
            st.dataframe(df_p)
                
            # Waterfall-like budget consumption
            df_p_sorted = df_p.sort_values('B/C Ratio', ascending=False)
            df_p_sorted['Selected'] = df_p_sorted['ID'].isin(selected_ids) 
            st.subheader("Phân tích hiệu quả đầu tư")
            fig_bar = px.bar(df_p_sorted, x='Tên dự án', y='NPV', color='Selected', 
                             title="Xếp hạng dự án theo hiệu suất (B/C Ratio)")
            st.plotly_chart(fig_bar, use_container_width=True)
        except Exception as e:
            st.error(f"Lỗi: {e}")

    with tabs[5]:
        st.header("6. Thảo luận chính sách")
        st.markdown(r"""
        - **Dự án P13 (Bán dẫn):** Dù có NPV lớn nhất (35.000) nhưng nó thường bị loại nếu ngân sách thấp hoặc do ràng buộc kéo theo dự án P3 (18.000 tỷ).
        - **Logic ràng buộc:** Các điều kiện thực tế (An ninh QG) thường làm giảm NPV tối ưu nhưng đảm bảo tính ổn định của hệ thống.
        - **Đánh đổi:** Công cụ MIP giúp lượng hóa được chúng ta đang "hy sinh" bao nhiêu NPV để duy trì các ràng buộc logic hoặc an ninh.
        """)
        
    with tabs[6]:
        st.header("7. Tham khảo")
        st.markdown(r"""
        - **Williams, H. P. (2013):** Model Building in Mathematical Programming.
        - **Báo cáo định hướng đầu tư công nghệ 2026-2030.**
        - **PuLP Documentation:** Linear and Integer Programming in Python.
        """)

if __name__ == "__main__":
    render()
