import threading
import queue
import time
import random
from threading import Lock, Semaphore, Event


class Estoque:
    def __init__(self, capacidade=10):
        self.capacidade = capacidade
        self.fila = queue.Queue(maxsize=capacidade)
        self.lock = Lock()
        self.items_disponiveis = Semaphore(0)
        self.espacos_disponiveis = Semaphore(capacidade)
        self.print_lock = Lock()
        self.total_produzido = 0
        self.total_consumido = 0
        self.producao_completa = Event()

    def print_thread_safe(self, mensagem):
        with self.print_lock:
            print(f"[{time.strftime('%H:%M:%S')}] {mensagem}")
            print(
                f"Status: produzidos={self.total_produzido}, consumidos={self.total_consumido}, em estoque={self.fila.qsize()}")

    def armazenar(self, produtor_id, item_id):
        try:
            self.espacos_disponiveis.acquire()
            with self.lock:
                self.fila.put((produtor_id, item_id))
                self.total_produzido += 1
                self.print_thread_safe(f"Produtor {produtor_id} armazena item {item_id}")
            self.items_disponiveis.release()
        except Exception as e:
            self.print_thread_safe(f"Erro ao armazenar: {e}")

    def fornecer(self, consumidor_id):
        try:
            self.items_disponiveis.acquire()
            with self.lock:
                item = self.fila.get()
                self.total_consumido += 1
                self.print_thread_safe(f"Consumidor {consumidor_id} recebe item {item[1]} do produtor {item[0]}")
            self.espacos_disponiveis.release()
            return item
        except Exception as e:
            self.print_thread_safe(f"Erro ao fornecer: {e}")
            return None


class Produtor(threading.Thread):
    def __init__(self, produtor_id, estoque, max_items):
        super().__init__(name=f"Produtor-{produtor_id}")
        self.produtor_id = produtor_id
        self.estoque = estoque
        self.item_id = 0
        self.max_items = max_items
        self.items_produzidos = 0
        self.active = True

    def run(self):
        while self.active and self.items_produzidos < self.max_items:
            try:
                tempo_producao = random.uniform(0.5, 2)
                time.sleep(tempo_producao)
                self.item_id += 1
                self.estoque.armazenar(self.produtor_id, self.item_id)
                self.items_produzidos += 1
            except Exception as e:
                with self.estoque.print_lock:
                    print(f"Erro no produtor {self.produtor_id}: {e}")

        with self.estoque.print_lock:
            print(f"Produtor {self.produtor_id} encerrou após produzir {self.items_produzidos} items")

    def stop(self):
        self.active = False


class Consumidor(threading.Thread):
    def __init__(self, consumidor_id, estoque):
        super().__init__(name=f"Consumidor-{consumidor_id}")
        self.consumidor_id = consumidor_id
        self.estoque = estoque
        self.items_consumidos = 0
        self.active = True

    def run(self):
        while self.active:
            try:
                if self.estoque.producao_completa.is_set() and self.estoque.fila.empty():
                    break

                tempo_consumo = random.uniform(0.8, 3)
                item = self.estoque.fornecer(self.consumidor_id)
                if item:
                    self.items_consumidos += 1
                    time.sleep(tempo_consumo)
            except Exception as e:
                with self.estoque.print_lock:
                    print(f"Erro no consumidor {self.consumidor_id}: {e}")

        with self.estoque.print_lock:
            print(f"Consumidor {self.consumidor_id} encerrou após consumir {self.items_consumidos} items")

    def stop(self):
        self.active = False


def monitor_threads(produtores, consumidores, estoque):
    """Monitora as threads e garante consumo completo"""
    try:
        # Aguarda todos os produtores terminarem
        for produtor in produtores:
            produtor.join()

        # Sinaliza que a produção está completa
        estoque.producao_completa.set()

        # Aguarda todos os consumidores terminarem
        for consumidor in consumidores:
            consumidor.join()

    except KeyboardInterrupt:
        print("\nEncerrando o programa...")
        for thread in produtores + consumidores:
            thread.stop()


if __name__ == "__main__":
    # Configurações
    NUM_PRODUTORES = 3
    NUM_CONSUMIDORES = 2
    CAPACIDADE_ESTOQUE = 5
    TOTAL_ITEMS_POR_PRODUTOR = 10

    # Inicialização
    estoque = Estoque(capacidade=CAPACIDADE_ESTOQUE)

    # Cria produtores e consumidores
    produtores = [Produtor(i, estoque, TOTAL_ITEMS_POR_PRODUTOR) for i in range(NUM_PRODUTORES)]
    consumidores = [Consumidor(i, estoque) for i in range(NUM_CONSUMIDORES)]

    # Inicia todas as threads
    for thread in produtores + consumidores:
        thread.start()

    try:
        # Monitora até que todos os itens sejam consumidos
        monitor_threads(produtores, consumidores, estoque)
    finally:
        print("\nResumo final:")
        print(f"Total de itens produzidos: {estoque.total_produzido}")
        print(f"Total de itens consumidos: {estoque.total_consumido}")
        print(f"Items restantes no estoque: {estoque.fila.qsize()}")
        for p in produtores:
            print(f"Produtor {p.produtor_id} produziu {p.items_produzidos} items")
        for c in consumidores:
            print(f"Consumidor {c.consumidor_id} consumiu {c.items_consumidos} items")

        assert estoque.total_produzido == estoque.total_consumido, "Erro: Nem todos os itens foram consumidos!"