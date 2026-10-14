# REA-GRAPH-CAUSAL# Motor Matemático de Investigação Bayesiana com Mitigação Adversarial

Este repositório contém um protótipo conceitual em **Python puro** que demonstra o núcleo matemático para avaliar a veracidade de hipóteses de identidade em cenários de engenharia reversa e inteligência de ameaças, combatendo dados falsos-confiáveis e contaminações.

## Visão Geral do Código

O script implementa uma classe de avaliação baseada em **Razões de Verossimilhança Logarítmica (Log-Likelihood Ratios - LLR)** e lógica Bayesiana. O objetivo é evitar falhas comuns de agentes de IA — como aceitar passivamente dados manipulados (falsos-confiáveis) — aplicando penalizações formais de incerteza e ruído.

### Componentes Principais

1. **`Evidence` (Estrutura de Dados):**
   * `source_id`: Identificador único da fonte.
   * `source_reliability`: Grau histórico de confiabilidade da fonte $[0.0, 1.0]$.
   * `supports_hypothesis`: Booleano indicando se a evidência apoia ($True$) ou refuta ($False$) a hipótese.
   * `raw_strength`: Intensidade bruta do sinal relatado $[0.0, 1.0]$.
   * `is_adversarial_flag`: Sinalizador de detecção de anomalia, injeção ou comportamento adversarial.

2. **`BayesianEvidenceEngine` (O Motor):**
   * **Cálculo de LLR (`compute_llr`):** Converte a força do sinal ponderada pela confiabilidade da fonte em espaço logarítmico. Se a evidência possui a flag adversarial ativada, o sistema descarta o sinal positivo e aplica uma penalização severa de rejeição.
   * **Avaliação Global (`evaluate_investigation`):** Acumula os LLRs, separa o suporte positivo do refutador, calcula uma **penalização por contradição** (quando há sinais fortes colidindo) e converte o resultado final via função sigmoide para uma probabilidade a posteriori.

## Como Executar

Execute diretamente usando o interpretador Python padrão:

```bash
python3 motor_investigacao.py
```

## Interpretação dos Resultados
O motor emite quatro estados possíveis com base na probabilidade final $P(H|E)$:
* **`CONFIRMED`:** $P \ge 0.85$ (Alta certeza baseada em fontes confiáveis).
* **`REFUTED`:** $P \le 0.15$ (Rejeitado por forte refutação ou detecção de adulteração).
* **`AMBIGUOUS/UNKNOWN`:** Zona intermediária ou de alta contradição, forçando o sistema a abster-se de uma conclusão cega.
