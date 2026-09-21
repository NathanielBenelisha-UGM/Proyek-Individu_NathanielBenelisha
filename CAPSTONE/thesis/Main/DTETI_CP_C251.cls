\NeedsTeXFormat{LaTeX2e}[1995/12/01]
\ProvidesClass{UGMThesis}
              [2013/7/16 v0.1
			  UGM Thesis Class]
%% Based on Report class	
		  
\LoadClass[12pt,a4paper]{report}

%% =================================
%% Package Import

%%	Ukuran Margin UGM
\RequirePackage[a4paper, top=25mm, bottom=25mm, left=25mm, right=20mm]{geometry}

%% Penggunaan Huruf Times New Roman
\usepackage{savesym}
\usepackage{amsmath}
\savesymbol{iint}
\usepackage{mathptmx}
\restoresymbol{TXF}{iint}

%% Pengaturan TOC, LOF dan LOT
\usepackage[subfigure]{tocloft}
\usepackage{titletoc}

%% Pengaturan Spasi
\usepackage{setspace}

%% Underline
\usepackage[normalem]{ulem}

%% Bookmarks
\usepackage{hyperref}

%% Array Package
\usepackage{array}

%% Menghitung Total Halaman
\usepackage{lastpage}

%% Pengaturan Header dan Footer
\usepackage{fancyhdr}

\usepackage[table,xcdraw]{xcolor}

%% =================================
%% Untuk Bahasa
\RequirePackage[bahasa]{babel}

%% Untuk Mengganti Gaya Judul Bahasa
\RequirePackage{titlesec}

%% Untuk Menambahkan toc ke toc
\RequirePackage{tocbibind}

%% =================================
%% Some Customizations

%% Standarize Underline
\setlength{\ULdepth}{3pt}
\renewcommand{\ULthickness}{1.5pt}

%% Untuk Import Gambar
\RequirePackage{graphicx}
\graphicspath{ {../../fig/} }
\usepackage[export]{adjustbox}

%% Numbering : Equation
\numberwithin{equation}{chapter}
\renewcommand{\theequation}{\arabic{chapter}.\arabic{equation}}

%% Numbering : Figure
\renewcommand{\thefigure}{\arabic{chapter}.\arabic{figure}}

%% Numbering : Table
\renewcommand{\thetable}{\arabic{chapter}.\arabic{table}}

%% Caption : Algoritma
\RequirePackage{algorithm}
\renewcommand{\ALG@name}{Algoritme}

%% Table Command
\newcolumntype{L}[1]{>{\raggedright\let\newline\\\arraybackslash\hspace{0pt}}m{#1}}
\newcolumntype{C}[1]{>{\centering\let\newline\\\arraybackslash\hspace{0pt}}m{#1}}
\newcolumntype{R}[1]{>{\raggedleft\let\newline\\\arraybackslash\hspace{0pt}}m{#1}}
\newcolumntype{M}[1]{>{\raggedright\let\newline\\\arraybackslash\hspace{0pt}}p{#1}}
\newcolumntype{D}[1]{>{\centering\let\newline\\\arraybackslash\hspace{0pt}}p{#1}}

%% Pengaturan Header dan Footer
\fancypagestyle{fancymod}
{
	\fancyhf{}
	\renewcommand{\headrulewidth}{0pt}
	\fancyfoot[R]{\thepage}
}

%% Redefine the Plain Page Style
\fancypagestyle{plain}
{
	\fancyhf{}
	\renewcommand{\headrulewidth}{0pt}
	\fancyfoot[R]{\thepage}
}

%% =================================
%% Pengaturan di TOC (Table of Content)

%% Pengaturan jarak antara tulisan ''CHAPTER x'' dgn nama chapter di TOC
%% (CHAPTER <No> <\cftchapnumwidth> <Name>)
%\renewcommand{\cftchapnumwidth}{7em}

\renewcommand\cfttoctitlefont{\vspace{-0.8cm}\large\bfseries\centering\MakeUppercase}
\renewcommand\cftloftitlefont{\vspace{-0.8cm}\hspace{.1cm}\large\bfseries\centering\MakeUppercase}
\renewcommand\cftlottitlefont{\vspace{-0.8cm}\hspace{.1cm}\large\bfseries\centering\MakeUppercase}

\dottedcontents{chapter}[1.5cm]{}{1.5cm}{0.3pc}
\dottedcontents{section}[2.25cm]{}{.75cm}{0.3pc}
\dottedcontents{subsection}[3.25cm]{}{1cm}{0.3pc}

% Pengaturan Posisi Judul Chapter
\titlespacing*{\chapter}{0pt}{-2.5em}{20pt}

%% =================================
%% Pengaturan di LOF (List of Figure) dan LOT (List of Table)

\renewcommand{\cftfigfont}{Gambar }
\renewcommand{\cfttabfont}{Tabel }
\setlength{\cftfignumwidth}{1.1cm}
\setlength{\cfttabnumwidth}{1.1cm}
\renewcommand\cftdotsep{0.3}
\renewcommand{\cftfigleader}{\cftdotfill{\cftdotsep}}
\renewcommand{\cfttableader}{\cftdotfill{\cftdotsep}}
    
%% ==================================
%% Pembuatan Command

%% Judul Bahasa Indonesia
\newcommand\judul[1]{\renewcommand\@judul{#1}}
\newcommand\@judul{\@latex@error{"Judul Capstone" belum lengkap}\@ehc}

%% Nomor Dokumen
\newcommand\NoDok[1]{\renewcommand\@NoDok{#1}}
\newcommand\@NoDok{\@latex@error{Data "Nomor Dokumen" belum diinputkan}\@ehc}

%% Nomor Revisi
\newcommand\NoRev[1]{\renewcommand\@NoRev{#1}}
\newcommand\@NoRev{\@latex@error{Data "Nomor Revisi" belum diinputkan}\@ehc}

%% Data Mahasiswa Capstone : Mahasiswa 1
\newcommand\MHSA[4]{\renewcommand\@MHSANama{#1}
\renewcommand\@MHSANIM{#2}
\renewcommand\@MHSAProdiKonsentrasi{#3}
\renewcommand\@MHSAEmail{#4}}
\newcommand\@MHSANama{\@latex@error{Data "Mahasiswa 1" belum lengkap}\@ehc}
\newcommand\@MHSANIM{\@latex@error{Data "Mahasiswa 1" belum lengkap}\@ehc}
\newcommand\@MHSAProdiKonsentrasi{\@latex@error{Data "Mahasiswa 1" belum lengkap}\@ehc}
\newcommand\@MHSAEmail{\@latex@error{Data "Mahasiswa 1" belum lengkap}\@ehc}

%% Data Mahasiswa Capstone : Mahasiswa 2
\newcommand\MHSB[4]{\renewcommand\@MHSBNama{#1}
\renewcommand\@MHSBNIM{#2}
\renewcommand\@MHSBProdiKonsentrasi{#3}
\renewcommand\@MHSBEmail{#4}}
\newcommand\@MHSBNama{\@latex@error{Data "Mahasiswa 2" belum lengkap}\@ehc}
\newcommand\@MHSBNIM{\@latex@error{Data "Mahasiswa 2" belum lengkap}\@ehc}
\newcommand\@MHSBProdiKonsentrasi{\@latex@error{Data "Mahasiswa 2" belum lengkap}\@ehc}
\newcommand\@MHSBEmail{\@latex@error{Data "Mahasiswa 2" belum lengkap}\@ehc}

%% Data Mahasiswa Capstone : Mahasiswa 3
\newcommand\MHSC[4]{\renewcommand\@MHSCNama{#1}
\renewcommand\@MHSCNIM{#2}
\renewcommand\@MHSCProdiKonsentrasi{#3}
\renewcommand\@MHSCEmail{#4}}
\newcommand\@MHSCNama{\@latex@error{Data "Mahasiswa 3" belum lengkap}\@ehc}
\newcommand\@MHSCNIM{\@latex@error{Data "Mahasiswa 3" belum lengkap}\@ehc}
\newcommand\@MHSCProdiKonsentrasi{\@latex@error{Data "Mahasiswa 3" belum lengkap}\@ehc}
\newcommand\@MHSCEmail{\@latex@error{Data "Mahasiswa 3" belum lengkap}\@ehc}

%% Data Mahasiswa Capstone : Mahasiswa 4
\newcommand\MHSD[4]{\renewcommand\@MHSDNama{#1}
\renewcommand\@MHSDNIM{#2}
\renewcommand\@MHSDProdiKonsentrasi{#3}
\renewcommand\@MHSDEmail{#4}}
\newcommand\@MHSDNama{\@latex@error{Data "Mahasiswa 4" belum lengkap}\@ehc}
\newcommand\@MHSDNIM{\@latex@error{Data "Mahasiswa 4" belum lengkap}\@ehc}
\newcommand\@MHSDProdiKonsentrasi{\@latex@error{Data "Mahasiswa 4" belum lengkap}\@ehc}
\newcommand\@MHSDEmail{\@latex@error{Data "Mahasiswa 4" belum lengkap}\@ehc}

%% Data Mahasiswa Capstone : Mahasiswa 5
\newcommand\MHSE[4]{\renewcommand\@MHSENama{#1}
\renewcommand\@MHSENIM{#2}
\renewcommand\@MHSEProdiKonsentrasi{#3}
\renewcommand\@MHSEEmail{#4}}
\newcommand\@MHSENama{\@latex@error{Data "Mahasiswa 5" belum lengkap}\@ehc}
\newcommand\@MHSENIM{\@latex@error{Data "Mahasiswa 5" belum lengkap}\@ehc}
\newcommand\@MHSEProdiKonsentrasi{\@latex@error{Data "Mahasiswa 5" belum lengkap}\@ehc}
\newcommand\@MHSEEmail{\@latex@error{Data "Mahasiswa 5" belum lengkap}\@ehc}

%% Data Dosen Pembimbing
\newcommand\DPA[2]{\renewcommand\@DPANama{#1}
\renewcommand\@DPANIP{#2}}
\newcommand\@DPANama{\@latex@error{Data "Dosen Pembimbing" belum lengkap}\@ehc}
\newcommand\@DPANIP{\@latex@error{Data "Dosen Pembimbing" belum lengkap}\@ehc}

%% Tempat Pelaksanaan
\newcommand\Tempat[1]{\renewcommand\@Tempat{#1}}
\newcommand\@Tempat{\@latex@error{Data "Tempat Pelaksanaan" belum diinputkan}\@ehc}

%% Memperbarui Command "maketitle" untuk Membuat Halaman Judul hingga Catatan Revisi Dokumen 
\renewcommand\maketitle{%
    % Pengaturan Caption Gambar, Tabel dan Algoritme
    \captionsetup[figure]{labelfont={default},labelformat={default},labelsep=period,name={Gambar }}
    \captionsetup[table]{labelfont={default},labelformat={default},labelsep=period,name={Tabel }}
    \captionsetup[algorithm]{labelfont={bf},labelformat={default},labelsep=period,name={Algoritme }}
    
 	\let\footnotesize\normalsize
	\let\footnoterule\relax
	\let\footnote\thanks
	
	\global\let\thanks\relax
	\global\let\maketitle\relax
	\global\let\@thanks\@empty
	\global\let\@author\@empty
	\global\let\@date\@empty
	\global\let\title\relax
	\global\let\author\relax
	\global\let\date\relax
	\global\let\and\relax
  
	%% Setting Halaman Baru : Halaman Judul
	\clearpage
	\frontmatters
	\begin{center}%
		{\Large {\MakeUppercase{\textbf{\@judul}}} \par}%
		\vskip 5mm
		{\Large {\textbf{DOKUMEN C-251}} \par}%
		\vskip 15mm%
		
		\includegraphics[width=85mm]{Logo_UGM.pdf}
		\vskip 10mm%
		
		\singlespacing
		{\large {\textbf{Disusun Oleh :}} \par}%
		\vskip 5mm%
		
		\begin{table}[!ht]
			\begin{center}
			\begin{tabular}{l C{1cm} l}
				{\large {\textbf{\@MHSANama}} }	&	{}	&
				{\large {\textbf{\@MHSANIM}} }		\\
				{\large {\textbf{\@MHSBNama}} }	&	{}	&
				{\large {\textbf{\@MHSBNIM}} }		\\
				{\large {\textbf{\@MHSCNama}} }	&	{}	&
				{\large {\textbf{\@MHSCNIM}} }		\\
				{\large {\textbf{\@MHSDNama}} }	&	{}	&
				{\large {\textbf{\@MHSDNIM}} }		\\
				{\large {\textbf{\@MHSENama}} }	&	{}	&
				{\large {\textbf{\@MHSENIM}} }		\\
			\end{tabular}
			\end{center}
		\end{table}
		\vskip 8mm%
		
		\onehalfspacing
		{\large {\textbf{DOKUMENTASI \textit{CAPSTONE PROJECT}}} \par}%
		{\large {\textbf{DEPARTEMEN TEKNIK ELEKTRO DAN TEKNOLOGI INFORMASI}} \par}%
		{\large {\textbf{FAKULTAS TEKNIK}} \par}%
		{\large {\textbf{UNIVERSITAS GADJAH MADA}} \par}%
		{\large {\textbf{\number\year}}}%
	\end{center}\par
  	
  	  	%% Setting Halaman Baru : Halaman Pengesahan
  	\clearpage
  	\preface
	\addcontentsline{toc}{chapter}{HALAMAN PENGESAHAN}
	\setcounter{page}{2}%
    
    %% --- GANTI TABEL DENGAN SCAN PDF ---
	\begin{center}
		\begin{small}
            %% ---- JUDUL HALAMAN TETAP DIPERTAHANKAN ----
			{\large {\textbf{HALAMAN PENGESAHAN}} \par}%
    		\vskip 2em%
            
            %% Pastikan 'Scan_Pengesahan.pdf' sudah ada di folder 'fig'
		    \includegraphics[page=1, width=1\textwidth, trim=0 0 0 0, clip]{fig/Scan_Pengesahan.pdf}
		\end{small}
	\end{center} \par


	
		%% Setting Halaman Baru : Bukti Bebas Plagiasi
	\newpage
	\addcontentsline{toc}{chapter}{BUKTI BEBAS PLAGIASI}
	
	%% --- 1. Masukkan Halaman Pertama (Di Bawah Judul) ---
	\begin{center}%
	    {\large {\textbf{BUKTI BEBAS PLAGIASI}} \par}%
		\vskip 10mm%
		
		%% Ubah 'Bebas_Plagiasi.pdf' dengan nama file asli Anda
		\includegraphics[page=1, width=\textwidth, frame]{fig/Bebas_Plagiasi.pdf}%
	\end{center} \par
	
	%% --- 2. Masukkan Sisa Halamannya (Halaman 2 s/d 8) ---
	%% pages=2- artinya dari halaman 2 sampai halaman terakhir
	\includepdf[pages=2-, scale=0.9, pagecommand={}]{fig/Bebas_Plagiasi.pdf}

	
	% Pengaturan Judul TOC, LOF dan LOT
    \renewcommand{\contentsname}{{\uppercase{Daftar Isi}}}
    \renewcommand{\listfigurename}{{\uppercase{Daftar Gambar}}}
    \renewcommand{\listtablename}{{\uppercase{Daftar Tabel}}}
    
    %% Mengganti Nama Chapter untuk Daftar Pustaka
    \renewcommand\bibname{REFERENSI}
    
	%% Setting Halaman Baru : Daftar Isi, Daftar Gambar, dan Daftar Tabel
	\onehalfspacing{
    	% Daftar Isi
    	\newpage
    	\chapter*{ }
    	\centering
    	\vspace*{-5.5em}	%% Pengaturan jarak vertikal judul TOC dari atas kertas
    	\tableofcontents
    
    	% Daftar Gambar
    	\newpage
    	\chapter*{ }
    	\centering
    	\vspace*{-5.5em}	%% Pengaturan jarak vertikal judul LOF dari atas kertas
    	\listoffigures
    
    	% Daftar Tabel
    	\newpage
    	\chapter*{ }
    	\centering
    	\vspace*{-5.5em}	%% Pengaturan jarak vertikal judul LOT dari atas kertas
    	\listoftables
    }
    
    % Setting Halaman Baru :  Catatan Revisi Dokumen
    \begin{revisi}
        \noindent
    	\begin{longtable}{|D{1.5cm} | D{2.5cm} | M{11cm}|}
    		\hline
    			\textbf{VERSI}	& 
    			\textbf{TANGGAL} &
    			\multicolumn{1}{|D{11cm}|}{\textbf{PERBAIKAN}} \\
    		\hline
    		    % Catatan Revisi Ke-0
    			\input{../Catatan_Revisi/Revisi_00.tex}	% Catatan Pembuatan Dokumen
                \\
                \hline
    			%
    			% Catatan Revisi Ke-1 dan seterusnya
    			\ifnum\@NoRev>0
    			    \input{../Catatan_Revisi/Revisi_01.tex}	% Rincian Perbaikan Versi ke-1
                    \\
                    \hline
    			\fi
    			\ifnum\@NoRev>1
    			    \input{../Catatan_Revisi/Revisi_02.tex}	% Rincian Perbaikan Versi ke-2
                    \\
                    \hline
    			\fi
    			\ifnum\@NoRev>2
    			    \input{../Catatan_Revisi/Revisi_03.tex}	% Rincian Perbaikan Versi ke-3
                    \\
                    \hline
    			\fi
    			\ifnum\@NoRev>3
    			    \input{../Catatan_Revisi/Revisi_04.tex}	% Rincian Perbaikan Versi ke-4
                    \\
                    \hline
    			\fi
    			\ifnum\@NoRev>4
    			    \input{../Catatan_Revisi/Revisi_05.tex}	% Rincian Perbaikan Versi ke-5
                    \\
                    \hline
    			\fi
    			\ifnum\@NoRev>5
    			    \input{../Catatan_Revisi/Revisi_06.tex}	% Rincian Perbaikan Versi ke-6
                    \\
                    \hline
    			\fi
    			\ifnum\@NoRev>6
    			    \input{../Catatan_Revisi/Revisi_07.tex}	% Rincian Perbaikan Versi ke-7
                    \\
                    \hline
    			\fi
    			\ifnum\@NoRev>7
    			    \input{../Catatan_Revisi/Revisi_08.tex}	% Rincian Perbaikan Versi ke-8
                    \\
                    \hline
    			\fi
    			\ifnum\@NoRev>8
    			    \input{../Catatan_Revisi/Revisi_09.tex}	% Rincian Perbaikan Versi ke-9
                    \\
                    \hline
    			\fi
    	\end{longtable}	
    \end{revisi}
    
    % Setting Halaman Baru : Intisari
    \begin{intisari}
        \setlength{\parindent}{20pt}
    	\input{Intisari.tex}
    \end{intisari}
    
    % Memulai Style Page Numbering yang Baru
    \clearpage
    \contents
}

%% Setting Environment Baru : Catatan Revisi Dokumen
\newenvironment{revisi}{%
	\newpage
	\addcontentsline{toc}{chapter}{CATATAN REVISI DOKUMEN}
	\@beginparpenalty\@lowpenalty
	\begin{center}%
		\bfseries \large\textbf{CATATAN REVISI DOKUMEN}
		\@endparpenalty\@M
	\end{center}}%
{\par\vfil\null}

%% Setting Environment Baru : Intisari
\newenvironment{intisari}{%
	\newpage
	\addcontentsline{toc}{chapter}{INTISARI}
	\singlespacing
	\@beginparpenalty\@lowpenalty
	\begin{center}%
		\bfseries \large\textbf{INTISARI}
		\@endparpenalty\@M
	\end{center}}%
{\par\vfil\null}

%% Setting Enviroment Baru : Ringkasan Eksekutif
\newenvironment{ringkasan}{%
	\newpage
	\addcontentsline{toc}{chapter}{RINGKASAN EKSEKUTIF}
	\@beginparpenalty\@lowpenalty
	\begin{center}%
		\bfseries \large\textbf{RINGKASAN EKSEKUTIF}
		\@endparpenalty\@M
	\end{center}}%
{\par\vfil\null}

%% Mengganti Gaya Penomoran Bab dan Subbab 
\renewcommand{\thechapter}{BAB \arabic{chapter}}
\renewcommand{\thesection}{\arabic{chapter}.\arabic{section}}
\renewcommand{\thesubsection}{\arabic{chapter}.\arabic{section}.\arabic{subsection}}

%% Mengganti Setting Page Numbering
% Menghilangkan Nomor Halaman pada Halaman Cover
\newcommand\frontmatters{\pagestyle{empty}}
% Memulai Nomor Halaman pada Halaman Pengesahan
\newcommand\preface{\pagestyle{fancymod} \pagenumbering{roman} \doublespacing}
% Memulai Nomor Halaman pada Isi Laporan
\newcommand\contents{\pagestyle{fancymod} \pagenumbering{arabic} \onehalfspacing}

%% Mengganti Gaya Titling Bab dan Subbab
\titleformat{\chapter}[block]
{\bfseries\filcenter\large}{\thechapter}{0.5em}{\\ \MakeUppercase}
\titleformat{\section}[hang]
{\bfseries}{\thesection}{0.5em}{}
\titleformat{\subsection}[hang]
{\bfseries}{\thesubsection}{0.5em}{}