from abc import ABC, abstractmethod

from .CPUEventBus import CPUEventBus


class CPUEventSubscriber(ABC):
    """
    Contrato de Infraestructura. 
    Define CÓMO un componente externo se engancha al sistema de eventos.
    """

    @abstractmethod
    def subscribe_to(self, bus: CPUEventBus) -> None:
        """
        Este método DEBE ser implementado para mapear 
        eventos a métodos privados de la clase.
        """
        pass