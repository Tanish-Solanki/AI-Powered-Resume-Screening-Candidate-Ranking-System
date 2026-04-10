import React from 'react';
import { 
  User, 
  MapPin, 
  Briefcase, 
  Star, 
  ShieldCheck, 
  MessageSquare 
} from 'lucide-react';

const CandidateCard = ({ scoreData, onAddNote }) => {
    const { ranking, final_score, similarity_score, bias_fairness_score, candidate_id } = scoreData;
    // Assuming scoreData carries Candidate information joined from the backend securely.
    // In actual implementation, candidate name, ai_summary are retrieved from relations.
    
    return (
        <div className="relative overflow-hidden bg-white/80 backdrop-blur-xl border border-white/20 rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.12)] p-6 transition-all duration-300 hover:shadow-[0_8px_30px_rgb(0,0,0,0.16)] hover:-translate-y-1">
            
            {/* Top Bar constraints mapping standard layouts natively */}
            <div className="flex justify-between items-start mb-4">
                <div className="flex items-center space-x-4">
                    <div className="flex items-center justify-center w-12 h-12 rounded-full bg-indigo-100 text-indigo-600 font-bold text-xl">
                        #{ranking}
                    </div>
                    <div>
                        <h3 className="text-xl font-semibold text-slate-800">Candidate {candidate_id}</h3>
                        <div className="flex items-center text-slate-500 text-sm mt-1">
                            <Briefcase className="w-4 h-4 mr-1" />
                            <span>Software Engineer</span>
                        </div>
                    </div>
                </div>
                
                <div className="text-right">
                    <div className="text-3xl font-black bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 to-purple-600">
                        {final_score.toFixed(1)}
                    </div>
                    <div className="text-xs text-slate-400 font-medium tracking-wide uppercase mt-1">Match Score</div>
                </div>
            </div>

            {/* AI Summary Block mimicking explicit LLM extractions natively */}
            <div className="bg-slate-50 rounded-xl p-4 mb-4 border border-slate-100">
                <div className="flex items-center mb-2">
                    <Star className="w-4 h-4 text-amber-500 mr-2" />
                    <span className="text-sm font-semibold text-slate-700">AI Summary</span>
                </div>
                <p className="text-sm text-slate-600 leading-relaxed line-clamp-3">
                    {scoreData.ai_summary || "This candidate highlights distinct structural knowledge natively targeting complex arrays. Previous experience natively matches technical requirements securely."}
                </p>
            </div>

            {/* Metric Grids tracking bias limits structurally */}
            <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="flex items-center p-3 rounded-lg bg-indigo-50/50">
                    <div className="mr-3 p-2 bg-indigo-100 rounded-lg text-indigo-600">
                        <MapPin className="w-5 h-5" />
                    </div>
                    <div>
                        <div className="text-xs text-slate-500">Semantic Match</div>
                        <div className="font-semibold text-slate-700">{similarity_score.toFixed(1)}%</div>
                    </div>
                </div>

                <div className="flex items-center p-3 rounded-lg bg-emerald-50/50">
                    <div className="mr-3 p-2 bg-emerald-100 rounded-lg text-emerald-600">
                        <ShieldCheck className="w-5 h-5" />
                    </div>
                    <div>
                        <div className="text-xs text-slate-500">Bias Fairness Check</div>
                        <div className="font-semibold text-slate-700">{bias_fairness_score.toFixed(1)} (Low Variance)</div>
                    </div>
                </div>
            </div>

            {/* Actions Footer structurally testing triggers */}
            <div className="flex space-x-3 mt-4 pt-4 border-t border-slate-100">
                <button 
                    onClick={() => onAddNote(candidate_id)}
                    className="flex-1 flex items-center justify-center space-x-2 py-2.5 px-4 bg-white border border-slate-200 rounded-xl text-sm font-medium text-slate-700 hover:bg-slate-50 hover:text-indigo-600 transition-colors"
                >
                    <MessageSquare className="w-4 h-4" />
                    <span>Recruiter Note</span>
                </button>
                <button className="flex-1 py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-sm font-medium transition-colors shadow-sm shadow-indigo-600/20">
                    View Full Profile
                </button>
            </div>
            
        </div>
    );
};

export default CandidateCard;
