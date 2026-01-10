import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  AreaChart, Area 
} from 'recharts';
import { 
  TrendingDown, TrendingUp, AlertCircle, Zap, Power, Play, 
  Settings, Bell, Volume2, VolumeX, Clock, Database, Search, 
  Menu, X, ChevronRight, Award
} from 'lucide-react';

// --- 상수 및 가상 데이터 생성 ---
const KOSPI_NAMES = ["삼성전자", "SK하이닉스", "LG에너지솔루션", "삼성바이오로직스", "현대차", "기아", "셀트리온", "POSCO홀딩스", "NAVER", "LG화학", "삼성SDI", "KB금융", "카카오", "신한지주", "현대모비스", "포스코퓨처엠", "삼성물산", "LG전자", "카카오뱅크", "SK이노베이션", "삼성생명", "LG생활건강", "HMM", "한국전력", "삼성전기"];
const KOSDAQ_NAMES = ["에코프로비엠", "에코프로", "HLB", "알테오젠", "HPSP", "엔켐", "셀트리온제약", "레인보우로보틱스", "리노공업", "신성델타테크", "솔브레인", "카카오게임즈", "펄어비스", "JYP Ent.", "위메이드", "클래시스", "동진쎄미켐", "에스엠", "엘앤에프", "리가켐바이오"];

const generateInitialStocks = (names, type) => {
  return names.map((name, idx) => {
    const price = Math.floor(Math.random() * 500000) + 5000;
    const ma25 = price * (1 + (Math.random() * 0.4 - 0.1)); 
    const deviation = ((price - ma25) / ma25) * 100;
    return {
      id: `${type}-${idx}-${name}-${Math.random().toString(36).substr(2, 5)}`,
      name,
      symbol: (100000 + (type === 'KOSPI' ? 0 : 5000) + idx).toString(),
      price,
      change: (Math.random() * 10 - 5).toFixed(2),
      volume: Math.floor(Math.random() * 1000000),
      ma25: Math.floor(ma25),
      deviation: parseFloat(deviation.toFixed(2)),
      rsi: Math.floor(Math.random() * 60) + 20,
      macd: Math.random() > 0.5 ? 'Golden' : 'Stable',
      type
    };
  });
};

const App = () => {
  // --- 상태 관리 ---
  const [isOnline, setIsOnline] = useState(true);
  const [isLiveMode, setIsLiveMode] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [stocks, setStocks] = useState([]);
  const [selectedStock, setSelectedStock] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [showJackpot, setShowJackpot] = useState(false);
  const [jackpotStock, setJackpotStock] = useState(null);
  
  // 이미 알림이 나간 종목을 추적하기 위한 Ref (중복 알림 도배 방지)
  const alertedStocksRef = useRef(new Set());

  // --- 초기화 ---
  useEffect(() => {
    const kospi = generateInitialStocks(KOSPI_NAMES, "KOSPI");
    const kosdaq = generateInitialStocks(KOSDAQ_NAMES, "KOSDAQ");
    setStocks([...kospi, ...kosdaq]);

    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // --- 알림 생성 함수 (Error Fix: crypto.randomUUID 사용) ---
  const triggerAlert = useCallback((stock, type, message) => {
    // 중복 키 에러 방지를 위해 확실한 고유 ID 생성
    const uniqueId = typeof crypto.randomUUID === 'function' 
      ? crypto.randomUUID() 
      : `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    const newAlert = { 
      id: uniqueId, 
      stockId: stock.id,
      stockName: stock.name, 
      type, 
      message, 
      time: new Date().toLocaleTimeString('ko-KR', { hour12: false }) 
    };
    
    setAlerts(prev => [newAlert, ...prev].slice(0, 20));
    
    if (!isMuted) {
      // 오디오 시뮬레이션
      console.log(`%c[${type}] ${stock.name}: ${message}`, "color: #2dd4bf; font-weight: bold;");
    }
  }, [isMuted]);

  // --- 1. 가격 및 데이터 시뮬레이션 (순수 데이터 업데이트) ---
  useEffect(() => {
    if (!isOnline) return;

    const interval = setInterval(() => {
      setStocks(prev => prev.map(stock => {
        const volatility = isLiveMode ? 0.02 : 0.01;
        const changeFactor = (Math.random() - 0.5) * volatility;
        const newPrice = Math.max(500, Math.floor(stock.price * (1 + changeFactor)));
        const newDeviation = ((newPrice - stock.ma25) / stock.ma25) * 100;
        
        return {
          ...stock,
          price: newPrice,
          deviation: parseFloat(newDeviation.toFixed(2)),
          rsi: Math.max(5, Math.min(95, stock.rsi + (Math.random() * 4 - 2))),
          volume: stock.volume + Math.floor(Math.random() * 10000)
        };
      }));
    }, 3000);

    return () => clearInterval(interval);
  }, [isOnline, isLiveMode]);

  // --- 2. 전략 감시 로직 (별도 Effect로 분리하여 안정성 확보) ---
  useEffect(() => {
    if (!isOnline || stocks.length === 0) return;

    stocks.forEach(stock => {
      // BNF 전략: 이격도 -20% 이하 급락 종목 감시
      if (stock.deviation < -20) {
        // 동일 종목에 대해 1분 이내 중복 알림 방지 로직 (간소화)
        const alertKey = `${stock.id}-BUY`;
        if (!alertedStocksRef.current.has(alertKey)) {
          triggerAlert(stock, "BUY", `이격도 ${stock.deviation}% 발생! 과매도 반등 신호`);
          alertedStocksRef.current.add(alertKey);
          
          // 30초 후 해당 종목 다시 알림 가능하게 초기화
          setTimeout(() => alertedStocksRef.current.delete(alertKey), 30000);
        }
      }

      // BNF 99% 잭팟 모드: 극심한 이격 (-30% 이하) + 낮은 RSI
      if (stock.deviation < -30 && stock.rsi < 20 && !showJackpot && Math.random() > 0.95) {
        setJackpotStock(stock);
        setShowJackpot(true);
      }
    });
  }, [stocks, isOnline, showJackpot, triggerAlert]);

  // --- 정렬된 데이터 ---
  const kospi50 = useMemo(() => 
    stocks.filter(s => s.type === "KOSPI").sort((a, b) => b.volume - a.volume).slice(0, 50)
  , [stocks]);

  const kosdaq50 = useMemo(() => 
    stocks.filter(s => s.type === "KOSDAQ").sort((a, b) => b.volume - a.volume).slice(0, 50)
  , [stocks]);

  // --- 카드 컴포넌트 ---
  const StatCard = React.memo(({ stock }) => (
    <div 
      className={`relative overflow-hidden p-4 rounded-2xl transition-all duration-500 cursor-pointer border
        ${stock.deviation < -20 
          ? 'bg-slate-900 border-rose-500 shadow-[0_0_25px_rgba(244,63,94,0.3)] scale-[1.02]' 
          : 'bg-slate-900/60 border-slate-700/50 hover:border-teal-500/50 hover:bg-slate-900 shadow-xl'}
      `}
      onClick={() => setSelectedStock(stock)}
    >
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="text-white font-black text-lg tracking-tighter">{stock.name}</h3>
          <span className="text-slate-500 text-[10px] font-mono tracking-widest">{stock.symbol}</span>
        </div>
        <div className={`px-2 py-0.5 rounded text-[9px] font-black ${stock.type === 'KOSPI' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' : 'bg-teal-500/20 text-teal-400 border border-teal-500/30'}`}>
          {stock.type}
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex justify-between items-end">
          <span className="text-2xl font-black text-white tabular-nums">{stock.price.toLocaleString()}</span>
          <span className={`text-xs font-bold tabular-nums ${parseFloat(stock.change) >= 0 ? 'text-rose-500' : 'text-blue-400'}`}>
            {stock.change}%
          </span>
        </div>
        
        <div>
          <div className="flex justify-between text-[9px] font-bold text-slate-500 mb-1 uppercase tracking-tighter">
            <span>25MA 이격도</span>
            <span className={stock.deviation < -20 ? 'text-rose-400 font-black animate-pulse' : ''}>{stock.deviation}%</span>
          </div>
          <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden border border-slate-700/50">
            <div 
              className={`h-full transition-all duration-1000 ease-out ${stock.deviation < -20 ? 'bg-gradient-to-r from-rose-600 to-rose-400' : 'bg-gradient-to-r from-teal-600 to-teal-400'}`}
              style={{ width: `${Math.min(Math.abs(stock.deviation) * 2.5, 100)}%` }}
            />
          </div>
        </div>

        <div className="flex gap-4 pt-1">
          <div className="flex flex-col">
            <span className="text-[9px] text-slate-500 font-black">RSI</span>
            <span className={`text-xs font-black ${stock.rsi < 30 ? 'text-teal-400 underline decoration-teal-500/50 underline-offset-2' : 'text-white'}`}>{Math.round(stock.rsi)}</span>
          </div>
          <div className="flex flex-col">
            <span className="text-[9px] text-slate-500 font-black text-right">VOL</span>
            <span className="text-xs font-black text-white text-right">{(stock.volume / 1000).toFixed(0)}K</span>
          </div>
        </div>
      </div>
      
      {stock.deviation < -20 && (
        <div className="absolute top-0 right-0">
          <div className="bg-rose-500 text-white text-[8px] font-black px-2 py-1 rounded-bl-xl shadow-lg animate-bounce">
            BNF BUY
          </div>
        </div>
      )}
    </div>
  ));

  return (
    <div className="min-h-screen bg-[#020617] text-slate-200 font-sans selection:bg-teal-500/30 overflow-x-hidden">
      {/* --- 상단 헤더 --- */}
      <header className="sticky top-0 z-50 bg-[#020617]/90 backdrop-blur-2xl border-b border-slate-800/80 px-6 py-4 flex flex-wrap items-center justify-between gap-6 shadow-[0_10px_30px_rgba(0,0,0,0.5)]">
        <div className="flex items-center gap-4">
          <div className="w-11 h-11 bg-gradient-to-tr from-teal-500 via-blue-600 to-rose-500 rounded-2xl flex items-center justify-center shadow-2xl shadow-teal-500/20 transform rotate-3">
            <Zap className="text-white fill-white" size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-black tracking-tighter bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">BNF RADAR <span className="text-teal-400 font-mono text-sm ml-1">PRO</span></h1>
            <div className="flex items-center gap-3 text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">
              <span className="flex items-center gap-1.5"><Clock size={12} className="text-teal-500" /> {currentTime.toLocaleTimeString('ko-KR', { hour12: false })}</span>
              <span className="w-1 h-1 bg-slate-700 rounded-full" />
              <span className={isOnline ? 'text-teal-400 animate-pulse' : 'text-rose-600'}>
                {isOnline ? '● Stream Active' : '○ Connection Lost'}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-5 bg-slate-900/60 p-2 rounded-2xl border border-slate-800/50 backdrop-blur-sm">
          <button 
            onClick={() => setIsLiveMode(!isLiveMode)}
            className={`px-5 py-2.5 rounded-xl text-[10px] font-black transition-all flex items-center gap-2 shadow-inner ${isLiveMode ? 'bg-rose-600 text-white shadow-rose-900/50' : 'bg-slate-800 text-slate-400'}`}
          >
            {isLiveMode ? <Database size={14} className="animate-spin-slow" /> : <Play size={14} />}
            {isLiveMode ? 'LIVE REAL-TIME' : 'SIMULATION MODE'}
          </button>
          <div className="h-8 w-px bg-slate-800" />
          <div className="flex items-center gap-4 px-2">
            <button onClick={() => setIsOnline(!isOnline)} className={`transition-all hover:scale-110 ${isOnline ? 'text-teal-400' : 'text-slate-700'}`}>
              <Power size={22} strokeWidth={3} />
            </button>
            <button onClick={() => setIsMuted(!isMuted)} className={`transition-all hover:scale-110 ${isMuted ? 'text-rose-500' : 'text-slate-400 hover:text-white'}`}>
              {isMuted ? <VolumeX size={22} strokeWidth={3} /> : <Volume2 size={22} strokeWidth={3} />}
            </button>
          </div>
        </div>
      </header>

      <main className="p-6 grid grid-cols-1 lg:grid-cols-12 gap-8 max-w-[1700px] mx-auto">
        
        {/* --- 메인 콘텐츠: 종목 그리드 --- */}
        <div className="lg:col-span-9 space-y-10">
          
          {/* 전략 헤드라인 */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-slate-900/40 border border-slate-800 p-5 rounded-3xl flex flex-col gap-3">
              <div className="flex items-center gap-3 text-teal-400">
                <TrendingDown size={24} />
                <span className="font-black text-sm uppercase tracking-wider">이격도 전략</span>
              </div>
              <p className="text-[11px] text-slate-400 leading-relaxed font-medium">25일 이평선 대비 20~35% 하락한 과매도 구간에서 기술적 반등을 노리는 BNF의 핵심 기법입니다.</p>
            </div>
            <div className="bg-slate-900/40 border border-slate-800 p-5 rounded-3xl flex flex-col gap-3">
              <div className="flex items-center gap-3 text-rose-500">
                <Zap size={24} />
                <span className="font-black text-sm uppercase tracking-wider">거래량 폭증</span>
              </div>
              <p className="text-[11px] text-slate-400 leading-relaxed font-medium">가격 급락 후 거래량이 바닥을 찍고 횡보하거나, 첫 양봉이 강하게 출현하는 시점이 진입 타점입니다.</p>
            </div>
            <div className="bg-slate-900/40 border border-slate-800 p-5 rounded-3xl flex flex-col gap-3">
              <div className="flex items-center gap-3 text-blue-500">
                <Award size={24} />
                <span className="font-black text-sm uppercase tracking-wider">심리 판독</span>
              </div>
              <p className="text-[11px] text-slate-400 leading-relaxed font-medium">군중의 공포가 극에 달할 때 독립적으로 판단하십시오. 익절은 감각으로, 손절은 기계적으로 실행합니다.</p>
            </div>
          </div>

          {/* KOSPI */}
          <section>
            <div className="flex items-center gap-4 mb-8">
              <div className="h-10 w-2.5 bg-blue-600 rounded-full shadow-[0_0_15px_rgba(37,99,235,0.6)]" />
              <div>
                <h2 className="text-3xl font-black tracking-tighter">KOSPI SELECTION</h2>
                <p className="text-slate-500 text-[10px] font-black uppercase tracking-widest">Top 50 Volume Leaders</p>
              </div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 2xl:grid-cols-5 gap-5">
              {kospi50.map(stock => <StatCard key={stock.id} stock={stock} />)}
            </div>
          </section>

          {/* KOSDAQ */}
          <section>
            <div className="flex items-center gap-4 mb-8 pt-4">
              <div className="h-10 w-2.5 bg-teal-500 rounded-full shadow-[0_0_15px_rgba(20,184,166,0.6)]" />
              <div>
                <h2 className="text-3xl font-black tracking-tighter">KOSDAQ SELECTION</h2>
                <p className="text-slate-500 text-[10px] font-black uppercase tracking-widest">Top 50 Volume Leaders</p>
              </div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 2xl:grid-cols-5 gap-5">
              {kosdaq50.map(stock => <StatCard key={stock.id} stock={stock} />)}
            </div>
          </section>
        </div>

        {/* --- 사이드바: 알림 및 리스크 관리 --- */}
        <aside className="lg:col-span-3 space-y-8 sticky top-28 h-fit">
          
          {/* 마켓 상태 정보 */}
          <div className="bg-slate-900 border border-slate-800 p-7 rounded-[2.5rem] shadow-2xl relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-32 h-32 bg-teal-500/5 blur-[60px] rounded-full" />
            <h3 className="text-xs font-black text-slate-500 uppercase tracking-[0.3em] mb-6 flex justify-between items-center">
              Market Health <Settings size={14} className="animate-spin-slow" />
            </h3>
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <span className="text-sm font-black text-slate-300">Trading Status</span>
                <span className="text-[10px] px-3 py-1 rounded-full bg-teal-500/10 text-teal-400 font-black border border-teal-500/20">OPERATIONAL</span>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-xs font-bold mb-2">
                  <span className="text-slate-400">Fear & Greed Index</span>
                  <span className="text-rose-500 italic">Extreme Fear</span>
                </div>
                <div className="h-2.5 w-full bg-slate-800 rounded-full overflow-hidden border border-slate-700/30 p-0.5">
                  <div className="h-full w-[17%] bg-gradient-to-r from-rose-700 via-rose-500 to-rose-400 rounded-full" />
                </div>
              </div>
              <div className="p-4 bg-slate-950/60 rounded-2xl border border-slate-800/50 shadow-inner">
                <p className="text-[11px] text-slate-500 italic leading-loose font-medium">
                  "시장의 노이즈를 제거하라. 25일 이동평균선과 현재가의 거리가 벌어질수록, 스프링은 더 강하게 튀어오른다."
                </p>
              </div>
            </div>
          </div>

          {/* 실시간 알림 피드 (Error Fixed: crypto.randomUUID IDs) */}
          <div className="bg-slate-900 border border-slate-800 p-7 rounded-[2.5rem] h-[580px] flex flex-col shadow-2xl relative">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xs font-black text-slate-500 uppercase tracking-[0.3em] flex items-center gap-2">
                <Bell size={18} className="text-teal-400" /> LIVE SIGNALS
              </h3>
              <span className="text-[9px] bg-slate-800 px-2 py-0.5 rounded text-slate-400 font-mono">{alerts.length} signals</span>
            </div>
            <div className="flex-1 overflow-y-auto space-y-4 pr-1 scrollbar-hide">
              {alerts.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-slate-700">
                  <Search size={40} className="opacity-10 mb-4" />
                  <span className="text-xs font-black italic tracking-widest opacity-30 uppercase">Waiting for signal...</span>
                </div>
              ) : (
                alerts.map(alert => (
                  <div 
                    key={alert.id} 
                    className="p-4 bg-slate-800/40 border border-slate-700/30 rounded-2xl animate-in slide-in-from-right-4 duration-500 group hover:border-teal-500/40 transition-colors shadow-lg"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-sm font-black text-white group-hover:text-teal-400 transition-colors">{alert.stockName}</span>
                      <span className="text-[9px] text-slate-600 font-mono font-black">{alert.time}</span>
                    </div>
                    <p className={`text-[11px] font-bold leading-relaxed ${alert.type === 'BUY' ? 'text-teal-400' : 'text-rose-400'}`}>
                      {alert.message}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* 기계적 리스크 관리 배너 */}
          <div className="bg-gradient-to-br from-rose-950/40 to-rose-900/20 border border-rose-500/30 p-6 rounded-[2.5rem] shadow-xl border-dashed">
            <div className="flex items-center gap-3 text-rose-500 mb-4">
              <div className="p-1.5 bg-rose-500/20 rounded-lg"><AlertCircle size={20} /></div>
              <span className="font-black text-xs uppercase tracking-widest">Risk Management</span>
            </div>
            <p className="text-[11px] leading-relaxed text-slate-400 font-bold">
              손절은 지능의 척도입니다. 예상 범위를 벗어난 가격 움직임에는 이유가 없어도 즉시 대응하십시오. 생존이 먼저입니다.
            </p>
          </div>

        </aside>
      </main>

      {/* --- 모달 시스템 --- */}
      
      {/* 99% 확신 종목 잭팟 팝업 */}
      {showJackpot && jackpotStock && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/95 backdrop-blur-3xl animate-in fade-in duration-700">
          <div className="bg-gradient-to-b from-slate-900 via-slate-950 to-black border border-teal-500/40 w-full max-w-xl rounded-[4rem] overflow-hidden shadow-[0_0_120px_rgba(20,184,166,0.15)] relative">
            <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-transparent via-teal-500 to-transparent animate-pulse" />
            <div className="p-12">
              <button 
                onClick={() => setShowJackpot(false)}
                className="absolute top-10 right-10 text-slate-500 hover:text-white transition-all hover:rotate-90 scale-125"
              >
                <X size={32} strokeWidth={3} />
              </button>
              
              <div className="flex flex-col items-center text-center">
                <div className="w-28 h-28 bg-teal-500 rounded-full flex items-center justify-center mb-10 shadow-[0_0_60px_rgba(20,184,166,0.5)] animate-bounce border-4 border-teal-300/20">
                  <TrendingUp size={56} className="text-white drop-shadow-lg" />
                </div>
                <h2 className="text-5xl font-black text-white mb-4 tracking-tighter italic italic">SYSTEM ALERT</h2>
                <p className="text-teal-400 font-black mb-12 uppercase tracking-[0.4em] text-sm flex items-center gap-3">
                   <span className="w-8 h-px bg-teal-500/50" /> BNF 99% PROBABILITY <span className="w-8 h-px bg-teal-500/50" />
                </p>
                
                <div className="w-full bg-white/5 rounded-[2.5rem] p-10 border border-white/5 shadow-2xl mb-12 backdrop-blur-sm">
                  <div className="flex justify-between items-end mb-8">
                    <div className="text-left">
                      <span className="text-slate-500 text-[10px] uppercase font-black tracking-widest block mb-2">Prime Target</span>
                      <h4 className="text-4xl font-black text-white">{jackpotStock.name}</h4>
                    </div>
                    <div className="text-right">
                      <span className="text-slate-500 text-[10px] uppercase font-black tracking-widest block mb-2">Deviation Gap</span>
                      <h4 className="text-4xl font-black text-rose-500 tabular-nums">{jackpotStock.deviation}%</h4>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-6">
                    <div className="bg-black/40 p-5 rounded-3xl border border-white/5">
                      <span className="block text-[9px] text-slate-500 font-black mb-1 uppercase tracking-widest">RSI Intensity</span>
                      <span className="text-2xl font-black text-teal-400">{Math.round(jackpotStock.rsi)} (Low)</span>
                    </div>
                    <div className="bg-black/40 p-5 rounded-3xl border border-white/5">
                      <span className="block text-[9px] text-slate-500 font-black mb-1 uppercase tracking-widest">Signal Strength</span>
                      <span className="text-2xl font-black text-white">MAXIMUM</span>
                    </div>
                  </div>
                </div>

                <button 
                  onClick={() => setShowJackpot(false)}
                  className="w-full py-6 bg-gradient-to-r from-teal-500 to-blue-600 hover:from-teal-400 hover:to-blue-500 text-black font-black text-2xl rounded-[2.5rem] transition-all shadow-[0_20px_50px_rgba(20,184,166,0.3)] hover:scale-[1.02] active:scale-[0.98] uppercase tracking-tighter"
                >
                  Confirm Execution
                </button>
                <p className="mt-8 text-[9px] text-slate-600 font-black uppercase tracking-[0.2em]">
                  Trade at your own risk • sense of volume required
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 상세 종목 분석 모달 */}
      {selectedStock && (
        <div className="fixed inset-0 z-[90] flex items-center justify-center p-6 bg-black/85 backdrop-blur-xl animate-in zoom-in-95 duration-300">
          <div className="bg-[#0f172a] border border-slate-700/50 w-full max-w-4xl rounded-[3rem] overflow-hidden shadow-[0_30px_60px_rgba(0,0,0,0.6)]">
            <div className="p-10 border-b border-slate-800 flex justify-between items-center bg-slate-900/30">
              <div className="flex items-center gap-5">
                <div className={`w-4 h-4 rounded-full ${selectedStock.type === 'KOSPI' ? 'bg-blue-600 shadow-[0_0_15px_rgba(37,99,235,0.8)]' : 'bg-teal-500 shadow-[0_0_15px_rgba(20,184,166,0.8)]'} animate-pulse`} />
                <div>
                  <h2 className="text-3xl font-black text-white tracking-tighter">{selectedStock.name}</h2>
                  <p className="text-slate-500 font-mono text-sm tracking-[0.2em]">{selectedStock.symbol} • ANALYSIS MODE</p>
                </div>
              </div>
              <button onClick={() => setSelectedStock(null)} className="p-3 text-slate-500 hover:text-white transition-all hover:bg-slate-800 rounded-2xl"><X size={32} strokeWidth={2} /></button>
            </div>
            <div className="p-10">
              <div className="h-80 w-full mb-10 bg-slate-950/40 rounded-[2.5rem] p-6 border border-slate-800/50">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={[
                    {t: '09:00', p: selectedStock.price * 0.94},
                    {t: '10:00', p: selectedStock.price * 0.89},
                    {t: '11:00', p: selectedStock.price * 0.85},
                    {t: '12:00', p: selectedStock.price * 0.82},
                    {t: '13:00', p: selectedStock.price * 0.88},
                    {t: '14:30', p: selectedStock.price * 0.95},
                    {t: '15:30', p: selectedStock.price}
                  ]}>
                    <defs>
                      <linearGradient id="detailGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#2DD4BF" stopOpacity={0.4}/>
                        <stop offset="95%" stopColor="#2DD4BF" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="4 4" stroke="#1e293b" vertical={false} opacity={0.3} />
                    <XAxis dataKey="t" stroke="#475569" fontSize={11} fontWeight="800" dy={10} />
                    <YAxis domain={['auto', 'auto']} stroke="#475569" fontSize={11} fontWeight="800" dx={-10} />
                    <Tooltip 
                      contentStyle={{backgroundColor: '#020617', border: '1px solid #334155', borderRadius: '20px', boxShadow: '0 20px 40px rgba(0,0,0,0.5)', padding: '15px'}}
                      itemStyle={{color: '#2DD4BF', fontWeight: '900'}}
                    />
                    <Area type="monotone" dataKey="p" stroke="#2DD4BF" strokeWidth={5} fillOpacity={1} fill="url(#detailGradient)" animationDuration={1500} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="p-7 bg-slate-900/50 rounded-3xl text-center border border-slate-800/50 group hover:border-teal-500/30 transition-all">
                  <span className="text-[10px] text-slate-500 block uppercase font-black mb-3 tracking-widest group-hover:text-teal-500 transition-colors">Market Price</span>
                  <span className="text-3xl font-black text-white tabular-nums">{selectedStock.price.toLocaleString()}</span>
                </div>
                <div className="p-7 bg-slate-900/50 rounded-3xl text-center border border-slate-800/50 group hover:border-teal-500/30 transition-all">
                  <span className="text-[10px] text-slate-500 block uppercase font-black mb-3 tracking-widest group-hover:text-teal-500 transition-colors">Vol Analytics</span>
                  <span className="text-3xl font-black text-white tabular-nums">{(selectedStock.volume / 1000).toFixed(1)}K</span>
                </div>
                <div className="p-7 bg-slate-900/50 rounded-3xl text-center border border-slate-800/50 group hover:border-rose-500/30 transition-all">
                  <span className="text-[10px] text-slate-500 block uppercase font-black mb-3 tracking-widest group-hover:text-rose-500 transition-colors">25MA Distance</span>
                  <span className={`text-3xl font-black tabular-nums ${selectedStock.deviation < -20 ? 'text-rose-500 animate-pulse' : 'text-teal-400'}`}>{selectedStock.deviation}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 푸터 영역 */}
      <footer className="p-16 border-t border-slate-900 bg-[#020617] text-center">
        <div className="flex flex-wrap justify-center gap-12 mb-10">
          <div className="flex flex-col items-center">
            <span className="text-[11px] font-black tracking-[0.4em] text-slate-600 uppercase mb-2">Architecture</span>
            <span className="text-xs font-bold text-slate-400">REACT 18 / TAILWIND 3</span>
          </div>
          <div className="flex flex-col items-center">
            <span className="text-[11px] font-black tracking-[0.4em] text-slate-600 uppercase mb-2">Algorithm</span>
            <span className="text-xs font-bold text-slate-400">BNF MEAN REVERSION V2.5</span>
          </div>
          <div className="flex flex-col items-center">
            <span className="text-[11px] font-black tracking-[0.4em] text-slate-600 uppercase mb-2">Security</span>
            <span className="text-xs font-bold text-slate-400">NON-DUPLICATE KEY PROTOCOL</span>
          </div>
        </div>
        <p className="text-[10px] text-slate-700 max-w-4xl mx-auto uppercase leading-[2.5] font-black tracking-tight">
          본 시스템은 일본의 전설적 트레이더 BNF의 매매 철학을 시뮬레이션하기 위한 분석 도구입니다. 제공되는 모든 데이터는 가상의 시뮬레이션이며, 실제 투자 시에는 반드시 증권사의 공식 데이터를 활용하시기 바랍니다. 모든 투자 결과에 대한 책임은 본인에게 있습니다.
        </p>
        <div className="mt-10 flex justify-center opacity-20">
          <div className="w-1.5 h-1.5 bg-slate-700 rounded-full mx-1" />
          <div className="w-1.5 h-1.5 bg-slate-700 rounded-full mx-1" />
          <div className="w-1.5 h-1.5 bg-slate-700 rounded-full mx-1" />
        </div>
      </footer>
    </div>
  );
};

export default App;
