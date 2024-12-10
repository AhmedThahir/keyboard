;OPTIMIZATIONS START
#SingleInstance force
#NoEnv
#MaxHotkeysPerInterval 99000000
#HotkeyInterval 99000000
#KeyHistory 0
ListLines Off
Process, Priority, , A
SetBatchLines, -1
SetKeyDelay, -1, -1
SetMouseDelay, -1
SetDefaultMouseSpeed, 0
SetWinDelay, -1
SetControlDelay, -1
;SendMode Input
;OPTIMIZATIONS END

SC001::Esc
SC029::0
SC002::1
SC003::2
SC004::3
SC005::4
SC006::5
SC007::6
SC008::7
SC009::8
SC00a::9
SC00b::return
SC00c::return
SC00d::return

SC010::q
SC011::w
SC012::f
SC013::p
SC014::b
SC015::return ;[

SC016::j
SC017::l
SC018::u
SC019::y
SC01A::'
SC01B::\

SC01E::a
SC01F::r
SC020::s
SC021::t
SC022::g
SC023::return ;;
SC024::k
SC025::n
SC026::e
SC027::i
SC028::o
SC01C::Tab

SC02c::x
SC02d::c
SC02e::d
SC02f::v
SC030::z
SC031::return
SC032::m
SC033::h
SC034::,
SC035::.

LShift::return
RShift::return
LCtrl::return

SC00E::Capslock
SC03A::LShift

SC00F::return ; Tab
>!SC01E::Tab ; Alt Tab

; Ctrl Remap
$LAlt::
	KeyWait, LAlt, T0.2;
	if (NOT ErrorLevel)
		Send {BackSpace}
	Send {Blind}{LAlt up}
	return
+LAlt::Send ^{BackSpace}

; Enter Remap
$RAlt::
	KeyWait, RAlt, T0.2;
	if (NOT ErrorLevel)
		Send {Enter}
	Send {Blind}{RAlt up}
	return

^RAlt::Send ^{Enter}

+RAlt::Send +{Enter}
; LAlt
<!SC039::Send ^{Space}
<!LButton::Send {LAlt up}^{LButton}
<!RButton::Send {LAlt up}^{RButton}

<!WheelUp::Send {LAlt up}^{WheelUp}
<!WheelDown::Send {LAlt up}^{WheelDown}

<!SC002::Send ^{1}
<!SC003::Send ^{2}
<!SC004::Send ^{3}
<!SC005::Send ^{4}
<!SC006::Send ^{5}
<!SC007::Send ^{6}

<!RAlt::Send ^{Enter}
<!SC010::Send ^{q}
<!SC011::Send ^{w}
<!SC012::Send ^{f}
<!SC013::Send ^{p}
<!SC014::Send ^{b}
<!SC015::return
<!SC016::Send ^{j}
<!SC017::Send ^{l}
<!SC018::Send ^{+} ;Send ^{u}
<!SC019::Send ^{y}
<!SC01A::Send ^{'}
<!SC01B::\
<!SC02B::o ; because of different keyboad layouts

<!SC01E::Send ^{a}
<!SC01F::Send ^{r}
<!SC020::Send ^{s}
<!SC021::Send ^{t}
<!SC022::Send ^{g}
<!SC023::return
<!SC024::Send ^{k}
<!SC025::Send ^{n}
<!SC026::Send ^{-} ;Send ^{e}
<!SC027::Send ^{i}
<!SC028::Send ^{o}
<!SC01C::Send ^{Tab}

<!SC02c::Send ^{x}
<!SC02d::Send ^{c}
<!SC02e::Send ^{z} ; d
<!SC02f::Send ^{v}
<!SC030::Send ^{z}
<!SC031::Send ^{/}
<!SC032::Send ^{m}
<!SC033::Send ^{h}
<!SC034::Send ^{,}
<!SC035::Send ^{.}
<!RShift::return

; LAlt + Shift
<!+LButton::Send {LAlt up}^+{LButton}

<!+SC00F::Send ^+{Tab}
<!+SC010::Send ^+{q}
<!+SC011::Send ^+{w}
<!+SC012::Send ^+{f}
<!+SC013::Send ^+{p}
<!+SC014::Send ^+{b}
<!+SC015::Send ^+{j}
<!+SC016::Send ^+{l}
<!+SC017::Send ^+{u}
<!+SC018::Send ^+{y}
<!+SC019::Send ^+{'}
<!+SC01A::Send ^+{\}
<!+SC01B::return

<!+SC01E::Send ^+{a}
<!+SC01F::Send ^+{r}
<!+SC020::Send ^+{s}
<!+SC021::Send ^+{t}
<!+SC022::Send ^+{g}
<!+SC023::return
<!+SC024::Send ^+{k}
<!+SC025::Send ^+{n}
<!+SC026::Send ^+{e}
<!+SC027::Send ^+{i}
<!+SC028::Send ^+{o}
<!+SC01C::return

<!+SC02c::Send ^+{x}
<!+SC02d::Send ^+{c}
<!+SC02e::Send ^+{z} ; d
<!+SC02f::Send ^+{v}
<!+SC030::Send ^+{z}
<+!SC031::Send ^+{/}
<!+SC032::Send ^+{h}
<!+SC034::Send ^+{m}
<!+SC033::Send ^+{,}
<!+SC035::Send +^{.}

+SC039::Send {;}

; Shift - Force myself to avoid shift
+SC001::return
+SC002::return
+SC003::return
+SC004::return
+SC005::return
+SC006::return
+SC007::return

+SC008::return
+SC009::return
+SC00a::return
+SC00b::return
+SC00c::return
+SC00d::return

+SC034::return
+SC035::return

; RAlt
>!SC010::Send {#}
>!SC011::Send {:}
>!SC013::Send {{}
>!SC014::Send {``}

>!SC017::Send {}}
>!SC019::Send {"}
>!SC01A::Send {&}
>!SC01B::Send {|}

>!SC022::Send {[}
>!SC024::Send {]}

>!SC02c::Send {*}
>!SC02d::Send {/}
>!SC02e::Send {(}
>!SC02f::Send {=}

>!SC032::Send {AltDown}`;{AltUp} ; call hunt and peck; run C:\HuntAndPeck-1.6\hap.exe /hint 
>!SC033::Send {)}
>!SC034::Send {+}
>!SC035::Send {-}

>!SC039::Send {_}

>!SC018::Send {Up}
>!SC025::Send {Left}
>!SC026::Send {Down}
>!SC027::Send {Right}
>!SC028::Send {Delete}
>!SC01C::Send {Esc}

>!SC01F::Send {Home}	;r
>!SC021::Send {End}	;t
>!SC020::Send {WheelDown 2}
>!SC012::Send {WheelUp 2}
	
; Control
>!<!SC025::Send ^{Left}
>!<!SC026::Send ^{End} ; this is better cuz i don't use it very often
>!<!SC027::Send ^{Right}
>!<!SC018::Send ^{Home} ; this is better cuz i don't use it very often

; RAlt + LAlt
>!<!SC010::Send {1}
>!<!SC011::Send {2}
>!<!SC012::Send {3}
>!<!SC013::Send {4}
>!<!SC014::Send {5}

>!<!SC017::Send {^}
>!<!SC019::Send {~}

>!<!SC01E::Send {!}
>!<!SC01F::Send {@}
>!<!SC020::Send {$}
>!<!SC021::Send {0}

>!<!SC028::Send ^{Delete} ; +{Tab}

>!<!SC02c::Send {6}
>!<!SC02d::Send {7}
>!<!SC02e::Send {8}
>!<!SC02f::Send {9}
>!<!SC030::return
>!<!SC031::return

>!<!SC032::Send {`%}
>!<!SC033::Send {?}
>!<!SC034::Send {<}
>!<!SC035::Send {>}

; RAlt+LShift+bottom row fallback for 2 key rollover keyboards
>!+SC02c::Send {6}
>!+SC02d::Send {7}
>!+SC02e::Send {8}
>!+SC02f::Send {9}
>!+SC030::return
>!+SC031::return

>!+SC032::Send {`%}
>!+SC033::Send {?}
>!+SC034::Send {<}
>!+SC035::Send {>}


; Alt + Shift
>!+SC025::Send +{Left}
>!+SC026::Send +{Down}
>!+SC027::Send +{Right}
>!+SC018::Send +{Up}

>!+SC01F::Send +{Home}	;r
>!+SC021::Send +{End}	;t
>!+SC012::Send +^{Home}
>!+SC020::Send +^{End}

; Control + Shift
>!<!+SC025::Send ^+{Left}
>!<!+SC026::Send ^+{Down}
>!<!+SC027::Send ^+{Right}
>!<!+SC018::Send ^+{Up}

DllCall("Sleep",UInt,17) ;I just used the precise sleep function to wait exactly 17 milliseconds