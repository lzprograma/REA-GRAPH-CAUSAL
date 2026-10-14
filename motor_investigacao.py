import math
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Evidence:
    source_id: str
    source_reliability: float  # [0.0, 1.0] - Confiabilidade histórica da fonte
    supports_hypothesis: bool  # True se aponta para a identidade alvo, False se refuta
    raw_strength: float        # [0.0, 1.0] - Intensidade bruta do sinal relatado
    is_adversarial_flag: bool  # Indicador se há suspeita de contaminação/injeção

class BayesianEvidenceEngine:
    def __init__(self, prior_probability: float = 0.5):
        # Probabilidade a priori (P(H)) de a hipótese de identidade ser verdadeira
        self.prior = prior_probability

    def compute_llr(self, evidence: Evidence) -> float:
        """
        Calcula a Razão de Verossimilhança Logarítmica (LLR) para uma evidência.
        Fórmula baseada na confiabilidade da fonte e na força do sinal,
        incorporando uma penalização severa se houver bandeira adversarial.
        """
        if evidence.is_adversarial_flag:
            # Se detectado como dado falso-confiável, inverte ou zera o impacto lógico
            return -math.log(9.0) # Forte peso contra a validade da evidência

        # Evidência neutra ou fraca
        strength = max(0.01, min(0.99, evidence.raw_strength))
        
        # Ponderação Bayesiana baseada na confiabilidade da fonte
        # Se a fonte é muito confiável, o peso do LLR aumenta exponencialmente.
        weight = evidence.source_reliability
        
        if evidence.supports_hypothesis:
            # LLR positivo para apoio
            return weight * math.log(strength / (1.0 - strength))
        else:
            # LLR negativo para refutação
            return -weight * math.log(strength / (1.0 - strength))

    def evaluate_investigation(self, evidences: List[Evidence]) -> Dict:
        """
        Acumula os LLRs e calcula a probabilidade a posteriori P(H | E_1, ..., E_n)
        juntamente com métricas de contradição e incerteza.
        """
        total_llr = math.log(self.prior / (1.0 - self.prior))
        support_sum = 0.0
        refute_sum = 0.0
        contradiction_penalty = 0.0

        for ev in evidences:
            llr = self.compute_llr(ev)
            total_llr += llr
            
            if llr > 0:
                support_sum += llr
            else:
                refute_sum += abs(llr)

        # Cálculo da penalização por contradição (quando há forças equilibradas de apoio e refutação)
        if support_sum > 0 and refute_sum > 0:
            balance = min(support_sum, refute_sum) / max(support_sum, refute_sum)
            # Se o sistema recebe dados que apoiam e refutam com a mesma intensidade, 
            # a incerteza explode, penalizando a certeza final.
            contradiction_penalty = balance * 2.0

        adjusted_llr = total_llr - contradiction_penalty

        # Conversão de volta para probabilidade [0, 1] usando a função sigmoide (inversa do logit)
        posterior = 1.0 / (1.0 + math.exp(-adjusted_llr))

        return {
            "prior": self.prior,
            "total_llr": total_llr,
            "contradiction_penalty": contradiction_penalty,
            "adjusted_llr": adjusted_llr,
            "posterior_probability": posterior,
            "decision": "CONFIRMED" if posterior >= 0.85 else ("REFUTED" if posterior <= 0.15 else "AMBIGUOUS/UNKNOWN")
        }

# --- Cenário Fictício de Demonstração ---
if __name__ == "__main__":
    print("--- SIMULAÇÃO MATEMÁTICA DE INVESTIGAÇÃO COM DADOS ADVERSARIAIS ---\n")
    
    # Conjunto de evidências recolhidas (incluindo um dado falso-confiável injetado)
    case_evidences = [
        Evidence(source_id="registry_primary", source_reliability=0.95, supports_hypothesis=True, raw_strength=0.90, is_adversarial_flag=False),
        Evidence(source_id="mirror_node_a", source_reliability=0.80, supports_hypothesis=True, raw_strength=0.75, is_adversarial_flag=False),
        # Dado falso-confiável: parece legítimo, mas o detetor identificou padrões de injeção adversarial
        Evidence(source_id="tainted_feed_x", source_reliability=0.90, supports_hypothesis=True, raw_strength=0.99, is_adversarial_flag=True),
        Evidence(source_id="static_analysis_log", source_reliability=0.85, supports_hypothesis=False, raw_strength=0.80, is_adversarial_flag=False)
    ]

    engine = BayesianEvidenceEngine(prior_probability=0.5)
    result = engine.evaluate_investigation(case_evidences)

    print(f"Probabilidade a Priori (P(H)): {result['prior']:.4f}")
    print(f"Soma LLR Bruta: {result['total_llr']:.4f}")
    print(f"Penalização por Contradição / Ruído: {result['contradiction_penalty']:.4f}")
    print(f"LLR Ajustado: {result['adjusted_llr']:.4f}")
    print(f"Probabilidade a Posteriori P(H|E): {result['posterior_probability']:.4f}")
    print(f"Decisão do Sistema: {result['decision']}")