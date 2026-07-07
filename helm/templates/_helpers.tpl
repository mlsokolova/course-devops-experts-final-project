{{/*
Expand the name of the chart.
*/}}
{{- define "quakewatch.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "quakewatch.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- define "quakewatch.configMapName" -}}
{{- .Values.configMap.name }}
{{- end }}

{{- define "quakewatch.secretName" -}}
{{- .Values.secret.name }}
{{- end }}

{{- define "quakewatch.quakewatchName" -}}
{{- .Values.quakewatch.name }}
{{- end }}

{{- define "quakewatch.duckdbName" -}}
{{- .Values.duckdb.name }}
{{- end }}

{{- define "quakewatch.duckdbServiceName" -}}
{{- .Values.duckdb.serviceName }}
{{- end }}

{{- define "quakewatch.image" -}}
{{- printf "%s:%s" .Values.image.repository .Values.image.tag }}
{{- end }}

{{- define "quakewatch.labels" -}}
helm.sh/chart: {{ include "quakewatch.name" . }}-{{ .Chart.Version | replace "+" "_" }}
app.kubernetes.io/name: {{ include "quakewatch.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "quakewatch.selectorLabels" -}}
app.kubernetes.io/name: {{ include "quakewatch.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
