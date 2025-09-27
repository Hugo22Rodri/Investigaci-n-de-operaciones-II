from django import forms

class ProblemSetupForm(forms.Form):
    origins = forms.IntegerField(
        label='Número de Orígenes', 
        min_value=1, 
        max_value=10,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    destinations = forms.IntegerField(
        label='Número de Destinos', 
        min_value=1, 
        max_value=10,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    is_balanced = forms.BooleanField(
        label='¿El problema está balanceado?', 
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class DataInputForm(forms.Form):
    def __init__(self, origins, destinations, *args, **kwargs):
        super(DataInputForm, self).__init__(*args, **kwargs)
        
        # Agregar campos para ofertas
        for i in range(origins):
            self.fields[f'supply_{i}'] = forms.IntegerField(
                label=f'Oferta del Origen {i+1}',
                min_value=0,
                widget=forms.NumberInput(attrs={'class': 'form-control', 'required': 'required'})
            )
        
        # Agregar campos para demandas
        for j in range(destinations):
            self.fields[f'demand_{j}'] = forms.IntegerField(
                label=f'Demanda del Destino {j+1}',
                min_value=0,
                widget=forms.NumberInput(attrs={'class': 'form-control', 'required': 'required'})
            )
        
        # Agregar campos para costos
        for i in range(origins):
            for j in range(destinations):
                self.fields[f'cost_{i}_{j}'] = forms.IntegerField(
                    label=f'Costo O{i+1}→D{j+1}',
                    min_value=0,
                    widget=forms.NumberInput(attrs={'class': 'form-control', 'required': 'required'})
                )