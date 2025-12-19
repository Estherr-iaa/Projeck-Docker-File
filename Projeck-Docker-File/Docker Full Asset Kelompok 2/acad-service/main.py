from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, Field
import psycopg2
import os
from datetime import datetime
from contextlib import contextmanager
import json

app = FastAPI(title="Product Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "acad-db"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "products"),
    "user": os.getenv("DB_USER", "productuser"),
    "password": os.getenv("DB_PASSWORD", "productpass"),
}


class Mahasiswa(BaseModel):
    nim: str
    nama: str
    jurusan: str
    angkatan: int = Field(ge=0)

@contextmanager
def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@app.on_event("startup")
async def startup_event():
    try:
        with get_db_connection():
            print("Acad Service: Connected to PostgreSQL")
    except Exception as e:
        print("PostgreSQL connection error:", e)


@app.get("/")
async def read_root(request: Request):
    session_data = request.cookies.get("session")
    
    if session_data:
        # User is logged in
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Dashboard Mahasiswa</title>
            <style>
                :root {
                    --primary-dark: #005461;
                    --primary: #018790;
                    --accent: #00B7B5;
                    --light-bg: #F4F4F4;
                }
                
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: var(--light-bg);
                    color: #333;
                }
                
                .header {
                    background-color: var(--primary-dark);
                    color: white;
                    padding: 15px 20px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .container {
                    max-width: 1200px;
                    margin: 20px auto;
                    padding: 20px;
                }
                
                .dashboard-card {
                    background-color: white;
                    padding: 25px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                }
                
                h1, h2 {
                    color: var(--primary-dark);
                    margin-top: 0;
                }
                
                .info-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin: 20px 0;
                }
                
                .info-item {
                    background-color: var(--light-bg);
                    padding: 15px;
                    border-radius: 5px;
                    text-align: center;
                }
                
                .info-label {
                    font-weight: bold;
                    color: var(--primary);
                    margin-bottom: 5px;
                }
                
                .info-value {
                    font-size: 1.2em;
                    color: var(--primary-dark);
                }
                
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }
                
                th, td {
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }
                
                th {
                    background-color: var(--primary);
                    color: white;
                }
                
                tr:hover {
                    background-color: var(--light-bg);
                }
                
                .logout-btn {
                    background-color: var(--primary);
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 14px;
                }
                
                .logout-btn:hover {
                    background-color: var(--accent);
                }
                
                @media (max-width: 768px) {
                    .info-grid {
                        grid-template-columns: 1fr;
                    }
                    
                    .header {
                        flex-direction: column;
                        text-align: center;
                    }
                    
                    .container {
                        padding: 15px;
                    }
                    
                    table {
                        font-size: 14px;
                    }
                    
                    th, td {
                        padding: 8px;
                    }
                }
                
                @media (max-width: 480px) {
                    table {
                        font-size: 12px;
                    }
                    
                    th, td {
                        padding: 6px;
                    }
                    
                    .dashboard-card {
                        padding: 15px;
                    }
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Dashboard Mahasiswa</h1>
                <button class="logout-btn" onclick="logout()">Logout</button>
            </div>
            
            <div class="container">
                <div class="dashboard-card">
                    <h2>Informasi Mahasiswa</h2>
                    <div class="info-grid">
                        <div class="info-item">
                            <div class="info-label">NIM</div>
                            <div class="info-value" id="nim-display">-</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Nama</div>
                            <div class="info-value" id="nama-display">-</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Jurusan</div>
                            <div class="info-value" id="jurusan-display">-</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">IPS</div>
                            <div class="info-value" id="ips-display">-</div>
                        </div>
                    </div>
                </div>
                
                <div class="dashboard-card">
                    <h2>Nilai Mata Kuliah</h2>
                    <table id="nilai-table">
                        <thead>
                            <tr>
                                <th>Kode MK</th>
                                <th>Nama Mata Kuliah</th>
                                <th>SKS</th>
                                <th>Nilai</th>
                                <th>Semester</th>
                            </tr>
                        </thead>
                        <tbody>
                            <!-- Nilai akan dimuat di sini -->
                        </tbody>
                    </table>
                </div>
            </div>

            <script>
                let nim = null;
                
                async function loadDashboard() {
                    try {
                        const urlParams = new URLSearchParams(window.location.search);
                        nim = urlParams.get('nim');
                        
                        if (!nim) {
                            window.location.href = '/login';
                            return;
                        }
                        
                        // Get student info and IPS
                        const ipsResponse = await fetch(`/api/acad/ips?nim=${nim}`);
                        const ipsData = await ipsResponse.json();
                        
                        document.getElementById('nim-display').textContent = ipsData.nim;
                        document.getElementById('nama-display').textContent = ipsData.nama;
                        document.getElementById('jurusan-display').textContent = ipsData.jurusan;
                        document.getElementById('ips-display').textContent = ipsData.ips;
                        
                        // Get all grades for this student
                        const nilaiResponse = await fetch(`/api/acad/nilai-matkul?nim=${nim}`);
                        const nilaiData = await nilaiResponse.json();
                        
                        const tbody = document.querySelector('#nilai-table tbody');
                        tbody.innerHTML = '';
                        
                        nilaiData.forEach(nilai => {
                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td>${nilai.kode_mk}</td>
                                <td>${nilai.nama_mk}</td>
                                <td>${nilai.sks}</td>
                                <td>${nilai.nilai}</td>
                                <td>${nilai.semester}</td>
                            `;
                            tbody.appendChild(row);
                        });
                        
                    } catch (error) {
                        console.error('Error loading dashboard:', error);
                        alert('Terjadi kesalahan saat memuat data');
                    }
                }
                
                function logout() {
                    document.cookie = "session=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
                    window.location.href = '/login';
                }
                
                document.addEventListener('DOMContentLoaded', loadDashboard);
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    else:
        # Redirect to login page
        return RedirectResponse(url="/login")


@app.get("/login")
async def login_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login Mahasiswa</title>
        <style>
            :root {
                --primary-dark: #005461;
                --primary: #018790;
                --accent: #00B7B5;
                --light-bg: #F4F4F4;
            }
            
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, var(--primary), var(--accent));
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            .login-container {
                background-color: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                width: 100%;
                max-width: 400px;
                text-align: center;
            }
            
            h1 {
                color: var(--primary-dark);
                margin-bottom: 30px;
            }
            
            .form-group {
                margin-bottom: 20px;
                text-align: left;
            }
            
            label {
                display: block;
                margin-bottom: 8px;
                color: var(--primary-dark);
                font-weight: bold;
            }
            
            input[type="text"], input[type="password"] {
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
                box-sizing: border-box;
            }
            
            input[type="text"]:focus, input[type="password"]:focus {
                border-color: var(--primary);
                outline: none;
            }
            
            .login-btn {
                background-color: var(--primary);
                color: white;
                border: none;
                padding: 15px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                width: 100%;
                margin-top: 10px;
            }
            
            .login-btn:hover {
                background-color: var(--accent);
            }
            
            .error-message {
                color: red;
                margin-top: 10px;
                display: none;
            }
            
            @media (max-width: 480px) {
                .login-container {
                    margin: 20px;
                    padding: 30px 20px;
                }
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h1>Login Mahasiswa</h1>
            <form id="loginForm">
                <div class="form-group">
                    <label for="nim">NIM:</label>
                    <input type="text" id="nim" name="nim" required>
                </div>
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="login-btn">Login</button>
            </form>
            <div id="errorMessage" class="error-message"></div>
        </div>

        <script>
            document.getElementById('loginForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const nim = formData.get('nim');
                const password = formData.get('password');
                
                // Check if NIM equals password
                if (nim !== password) {
                    document.getElementById('errorMessage').textContent = 'NIM dan Password harus sama!';
                    document.getElementById('errorMessage').style.display = 'block';
                    return;
                }
                
                try {
                    // Verify that the student exists in database
                    const response = await fetch(`/api/acad/ips?nim=${nim}`);
                    if (response.ok) {
                        // Create a simple session cookie
                        document.cookie = `session=${nim}; path=/;`;
                        window.location.href = `/?nim=${nim}`;
                    } else {
                        document.getElementById('errorMessage').textContent = 'NIM tidak ditemukan!';
                        document.getElementById('errorMessage').style.display = 'block';
                    }
                } catch (error) {
                    document.getElementById('errorMessage').textContent = 'Terjadi kesalahan!';
                    document.getElementById('errorMessage').style.display = 'block';
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# New endpoint to get all course grades for a student
@app.get("/api/acad/nilai-matkul")
async def get_nilai_matkul(nim: str = Query(..., description="NIM Mahasiswa")):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            query = """
                SELECT m.nama, mk.kode_mk, mk.nama_mk, mk.sks, krs.nilai, krs.semester
                FROM mahasiswa m
                JOIN krs ON krs.nim = m.nim
                JOIN mata_kuliah mk ON mk.kode_mk = krs.kode_mk
                WHERE m.nim = %s
                ORDER BY krs.semester, mk.kode_mk
            """

            cursor.execute(query, (nim,))
            rows = cursor.fetchall()

            if not rows:
                raise HTTPException(
                    status_code=404,
                    detail="Data mahasiswa tidak ditemukan"
                )

            return [
                {
                    "nim": row[0],  # This is actually the name, but we'll use the nim parameter
                    "kode_mk": row[1],
                    "nama_mk": row[2],
                    "sks": row[3],
                    "nilai": row[4],
                    "semester": row[5],
                }
                for row in rows
            ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {
        "status": "Acad Service is running",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/acad/mahasiswa")
async def get_mahasiswa():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM mahasiswa")
            rows = cursor.fetchall()

            return [
                {
                    "nim": row[0],
                    "nama": row[1],
                    "jurusan": row[2],
                    "angkatan": row[3],
                }
                for row in rows
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/acad/ips")
async def get_ips(
    nim: str = Query(..., description="NIM Mahasiswa")
):
    try:
        # tambahkan konfigurasi Anda di sini
        with get_db_connection() as conn:
            cursor = conn.cursor()

            query = """
                SELECT m.nim, m.nama, m.jurusan, krs.nilai, mk.sks
                FROM mahasiswa m
                JOIN krs ON krs.nim = m.nim
                JOIN mata_kuliah mk ON mk.kode_mk = krs.kode_mk
                WHERE m.nim = %s
            """

            cursor.execute(query, (nim,))
            rows = cursor.fetchall()

            if not rows:
                raise HTTPException(
                    status_code=404,
                    detail="Data mahasiswa tidak ditemukan"
                )

        # ambil data untuk nilai dan sks
        # jika A maka dikali 4, B+ dikali 3.5, B dikali 3,
        # B- dikali 2.75, C+ dikali 2.5, C dikali 2,
        # D dikali 1, E dikali 0
        nilai_bobot = {
            "A": 4.0,
            "A-": 3.75,
            "B+": 3.5,
            "B": 3.0,
            "B-": 2.75,
            "C+": 2.5,
            "C": 2.0,
            "D": 1.0,
            "E": 0.0,
        }

        total_sks = 0
        total_nilai = 0

        for row in rows:
            nilai = row[3]
            sks = row[4]
            bobot = nilai_bobot.get(nilai, 0)

            total_nilai += bobot * sks
            total_sks += sks

        if total_sks == 0:
            raise HTTPException(
                status_code=400,
                detail="Total SKS tidak boleh nol"
            )

        ips = total_nilai / total_sks

        return {
            "nim": rows[0][0],
            "nama": rows[0][1],
            "jurusan": rows[0][2],
            "ips": round(ips, 2),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))