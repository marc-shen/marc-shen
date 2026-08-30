<div align="center">

```
                                                  
 mm    mm            mmmm      mmmm               
 ##    ##            ""##      ""##               
 ##    ##   m####m     ##        ##       m####m  
 ########  ##mmmm##    ##        ##      ##"  "## 
 ##    ##  ##""""""    ##        ##      ##    ## 
 ##    ##  "##mmmm#    ##mmm     ##mmm   "##mm##" 
 ""    ""    """""      """"      """"     """"   
                                                  
                                                  
```

[![Typing SVG](https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=22&duration=3200&pause=900&color=00FF41&center=true&vCenter=true&width=520&lines=astronomy+student+%40+BNU;plasma+simulations+%26+fast+radio+bursts;Fortran+%2B+Python+%2B+too+many+dotfiles)](https://git.io/typing-svg)

[![Website](https://img.shields.io/badge/Website-songyushen.com-0D1117?style=flat-square&logo=githubpages&logoColor=00FF41)](https://songyushen.com/)
[![Blog](https://img.shields.io/badge/Blog-blog.stic.work-1F2430?style=flat-square&logo=astro&logoColor=FF5D01)](https://blog.stic.work)
![Profile views](https://komarev.com/ghpvc/?username=marc-shen&style=flat-square&color=00FF41&label=visitors)

</div>

---

```console
marc@bnu:~$ whoami --verbose
┌────────────────────────────────────────────────────────────┐
│  name      : Marc Shen (Songyu Shen)                       │
│  role      : Astronomy student, Beijing Normal University  │
│  location  : Beijing, China                                │
│  research  : PIC plasma simulations / Fast Radio Bursts    │
│  stack     : Fortran, Python, C++, Jupyter, LaTeX          │
│  editor    : Helix + VS Code (vim keys, always)            │
│  shell     : zsh + tmux, on macOS and HPC clusters         │
│  fun_fact  : I compile telescope software for fun          │
└────────────────────────────────────────────────────────────┘

marc@bnu:~$ cat /etc/motd
"Astronomy compels the soul to look upward,
 and leads us from this world to another." — Plato
```

---

```console
marc@bnu:~$ ls -la ~/projects --sort=recent
total 6
drwxr-xr-x  research/    empi-fortran/       # EM PIC solver, Fortran
drwxr-xr-x  research/    empi-work/          # analysis pipeline, Python
drwxr-xr-x  research/    pic-tristan/        # Tristan-MP setups
drwxr-xr-x  teaching/    computing-for-astronomy/
drwxr-xr-x  web/         dream-quest/        # blog.stic.work, Astro
drwxr-xr-x  web/         marc-shen.github.io/  # songyushen.com, Jekyll
```

| repo | what it is | stack |
|:--|:--|:--|
| [**EMPI-Fortran**](https://github.com/marc-shen/EMPI-Fortran) | Electromagnetic particle-in-cell solver written from scratch | `Fortran` `MPI` |
| [**EMPi**](https://github.com/marc-shen/EMPi) | Numerical modeling of plasma-induced effects on Fast Radio Bursts | `Jupyter` `Python` |
| [**empi-work**](https://github.com/marc-shen/empi-work) | Post-processing & visualization for the EMPi runs | `Python` `NumPy` |
| [**computing-for-astronomy**](https://github.com/marc-shen/computing-for-astronomy) | *Why Computing for Astronomy?* — notes & lectures | `Makefile` `LaTeX` |
| [**Dream-Quest**](https://github.com/marc-shen/Dream-Quest) | The way to Kadath — personal blog at [blog.stic.work](https://blog.stic.work) | `Astro` `TS` |
| [**marc-shen.github.io**](https://github.com/marc-shen/marc-shen.github.io) | Personal site at [songyushen.com](https://songyushen.com/) — Jekyll / minimal-mistakes | `Jekyll` `JS` |
| [**pic-tristan**](https://github.com/marc-shen/pic-tristan) | Tristan-MP setups & diagnostics for PIC experiments | `Fortran` |

---

<!--START_SECTION:waka-->

```console
marc@bnu:~$ gh-stats --summary
storage        926.5 MB
contributions  208 in 2026
public repos   9 (forks excluded)
member since   2019 (6 years)

marc@bnu:~$ gh-stats --commits --group-by=daypart
🌞 Morning                30 commits          █░░░░░░░░░░░░░░░░░░░░░░░░   05.42 % 
🌆 Daytime                132 commits         ██████░░░░░░░░░░░░░░░░░░░   23.87 % 
🌃 Evening                220 commits         ██████████░░░░░░░░░░░░░░░   39.78 % 
🌙 Night                  171 commits         ████████░░░░░░░░░░░░░░░░░   30.92 % 

marc@bnu:~$ gh-stats --commits --group-by=weekday
Monday                   109 commits         █████░░░░░░░░░░░░░░░░░░░░   19.71 % 
Tuesday                  100 commits         █████░░░░░░░░░░░░░░░░░░░░   18.08 % 
Wednesday                101 commits         █████░░░░░░░░░░░░░░░░░░░░   18.26 % 
Thursday                 91 commits          ████░░░░░░░░░░░░░░░░░░░░░   16.46 % 
Friday                   66 commits          ███░░░░░░░░░░░░░░░░░░░░░░   11.93 % 
Saturday                 32 commits          █░░░░░░░░░░░░░░░░░░░░░░░░   05.79 % 
Sunday                   54 commits          ██░░░░░░░░░░░░░░░░░░░░░░░   09.76 % 

marc@bnu:~$ cloc --no-web --no-notebooks ~/src
Python                   50,195 lines        █████████████████░░░░░░░░   69.20 % 
Fortran                  17,550 lines        ██████░░░░░░░░░░░░░░░░░░░   24.19 % 
Emacs Lisp               1,385 lines         ░░░░░░░░░░░░░░░░░░░░░░░░░   01.91 % 
CMake                    1,151 lines         ░░░░░░░░░░░░░░░░░░░░░░░░░   01.59 % 
Shell                    1,143 lines         ░░░░░░░░░░░░░░░░░░░░░░░░░   01.58 % 
Lua                      567 lines           ░░░░░░░░░░░░░░░░░░░░░░░░░   00.78 % 
MATLAB                   437 lines           ░░░░░░░░░░░░░░░░░░░░░░░░░   00.60 % 
make                     84 lines            ░░░░░░░░░░░░░░░░░░░░░░░░░   00.12 % 
DOS Batch                26 lines            ░░░░░░░░░░░░░░░░░░░░░░░░░   00.04 % 

marc@bnu:~$ date -u
Sun Aug 30 13:10:21 UTC 2026
```

<!--END_SECTION:waka-->

---

```console
marc@bnu:~$ ./snake --eat-contributions --loop
```

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/marc-shen/marc-shen/output/github-contribution-grid-snake-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/marc-shen/marc-shen/output/github-contribution-grid-snake.svg" />
  <img alt="github contribution grid snake animation" src="./game.svg" />
</picture>

</div>

---

```console
marc@bnu:~$ cat ~/.config/toolchain.txt
```

<div align="center">

![Python](https://img.shields.io/badge/Python-0D1117?style=for-the-badge&logo=python&logoColor=00FF41)
![Fortran](https://img.shields.io/badge/Fortran-0D1117?style=for-the-badge&logo=fortran&logoColor=00FF41)
![C++](https://img.shields.io/badge/C++-0D1117?style=for-the-badge&logo=cplusplus&logoColor=00FF41)
![NumPy](https://img.shields.io/badge/NumPy-0D1117?style=for-the-badge&logo=numpy&logoColor=00FF41)
![Jupyter](https://img.shields.io/badge/Jupyter-0D1117?style=for-the-badge&logo=jupyter&logoColor=00FF41)
![LaTeX](https://img.shields.io/badge/LaTeX-0D1117?style=for-the-badge&logo=latex&logoColor=00FF41)

![Linux](https://img.shields.io/badge/Linux-0D1117?style=for-the-badge&logo=linux&logoColor=00FF41)
![macOS](https://img.shields.io/badge/macOS-0D1117?style=for-the-badge&logo=apple&logoColor=00FF41)
![Git](https://img.shields.io/badge/Git-0D1117?style=for-the-badge&logo=git&logoColor=00FF41)
![Helix](https://img.shields.io/badge/Helix-0D1117?style=for-the-badge&logo=helix&logoColor=00FF41)
![Astro](https://img.shields.io/badge/Astro-0D1117?style=for-the-badge&logo=astro&logoColor=00FF41)
![Cloudflare](https://img.shields.io/badge/Cloudflare-0D1117?style=for-the-badge&logo=cloudflare&logoColor=00FF41)

</div>

---

<div align="center">

```console
marc@bnu:~$ exit
logout
Connection to github.com closed. Clear skies! 🔭
```

</div>
