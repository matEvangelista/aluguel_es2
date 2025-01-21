import datetime

class AluguelController:
    from datetime import datetime

    @staticmethod
    def calcula_valor_extra(dt1: datetime, dt2: datetime) -> int:
        """
        Função para calcular o valor da viagem.
        :param dt1: O primeiro datetime
        :param dt2: O segundo datetime
        :return: O número de "meias horas" entre os dois datetimes
        """
        # segundos
        delta = dt2 - dt1
        minutos = delta.total_seconds() / 60
        meias_horas = int(minutos // 30) # quantas "meias-horas" se passam
        return meias_horas*5
