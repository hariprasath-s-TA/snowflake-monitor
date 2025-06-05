import streamlit as st
import base64
logo_base64li = base64.b64encode(open("./Images/linkedin.png", "rb").read()).decode()
logo_base64tiger= base64.b64encode(open("./Images/tiger.webp", "rb").read()).decode()

@st.fragment
def footer():
    st.markdown("""<style>
            .footer {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background-color: #f1f1f1;
                padding: 3px 3px;  /* Reduced padding for a smaller height */
                font-size: 10px;  /* Reduced font size */
                color: #555;
                display: flex;
                justify-content: center;  /* Centers the content */
                align-items: center;
            }
            .footer .content {
                text-align: center;  /* Keeps the text in the center */
                flex-grow: 1;
            }
            .footer .logo-container {
                position: absolute;
                right: 20px;  /* Align the logos to the right */
                top: 50%;
                transform: translateY(-50%);
                display: flex;
                gap: 10px;  /* Space between logos */
            }
            .footer img {
                height: 20px;  /* Adjusted logo size for a smaller footer */
                vertical-align: middle;
            }</style>""", unsafe_allow_html=True)

    # Footer with 3 logos placed in the right corner and clickable links
    # Inject footer HTML with markdown
    st.markdown(f"""
        
        <div class="footer">
            <div class="content">
                <p>Copyright © 2025 Tiger Analytics | All rights reserved</p>
            </div>
            <div class="logo-container">
                <a href="https://www.tigeranalytics.com" target="_blank">
                    <img src="data:image/webp;base64,{logo_base64tiger}" >
                </a>
                <a href="https://in.linkedin.com/company/tiger-analytics" target="_blank">
                    <img src="data:image/png;base64,{logo_base64li}" >
                </a>
            </div>
        </div>
    """, unsafe_allow_html=True)