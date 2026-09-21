# Load Balancer Simulation

Simulação de um sistema de filas com três servidores e diferentes estratégias de balanceamento de carga.

## Pré-requisitos

- Python 3.9 ou superior
- `pip`

As dependências Python são:

- [SimPy](https://simpy.readthedocs.io/)
- [Matplotlib](https://matplotlib.org/)

## Instalação

No diretório do projeto, crie e ative um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instale as dependências:

```bash
python -m pip install simpy matplotlib
```

No Windows PowerShell, a ativação do ambiente virtual é feita com:

```powershell
.venv\Scripts\Activate.ps1
```

## Como executar

Com o ambiente virtual ativado, execute:

```bash
python main.py
```

A execução padrão simula:

- Lambdas de chegada: `0.6`, `1.2`, `1.8`, `2.4` e `2.7`
- Estratégias: `random`, `round_robin` e `shortest_queue`
- 10 seeds por configuração
- 3 servidores
- 5000 unidades de tempo de simulação
- 500 unidades de aquecimento (warm-up)

Isso resulta em 150 simulações. Durante a execução, o programa imprime o progresso e as métricas de cada configuração.

## Resultados

Os resultados são salvos no diretório `results/`:

- `metrics.csv`: médias e intervalos de confiança de 95% por configuração
- `metrics_throughput.png`: gráfico de throughput
- `metrics_expected_response_time.png`: gráfico de `E[R]`, incluindo a curva analítica fixa da estratégia random
- `metrics_average_requests_in_system.png`: gráfico do número médio de requisições no sistema
- `metrics_server_utilization.png`: gráfico da utilização de cada servidor

O diretório `results/` é criado automaticamente quando necessário.

## Configuração

Para alterar os parâmetros da bateria de testes, edite as constantes e listas no início de `main.py`, como:

- `lambdas`: valores de lambda de chegada
- `seeds`: seeds usadas nas réplicas
- `simulation_time`: duração de cada simulação
- `warmup_time`: período descartado antes da medição
- `RUN_LAMBDA_3_3`: habilita uma execução adicional para lambda `3.3`

Depois de alterar a configuração, execute novamente:

```bash
python main.py
```
