import { computed } from 'vue'

export type Unit = 'metric' | 'imperial'

export const CM_PER_IN = 2.54
export const KG_PER_LB = 0.45359237

export const cmToIn = (v: number | null): number | null => (v == null ? null : v / CM_PER_IN)
export const inToCm = (v: number | null): number | null => (v == null ? null : v * CM_PER_IN)
export const kgToLb = (v: number | null): number | null => (v == null ? null : v / KG_PER_LB)
export const lbToKg = (v: number | null): number | null => (v == null ? null : v * KG_PER_LB)

export const weightUnitLabel = (unit: Unit): string => (unit === 'imperial' ? 'lb' : 'kg')
export const cmUnitLabel = (unit: Unit): string => (unit === 'imperial' ? 'in' : 'cm')
export const heightUnitLabel = (unit: Unit): string => (unit === 'imperial' ? 'in' : 'cm')

export function dispValue(unit: Unit, metric: string, v: number | null): number | null {
  if (v == null) return null
  if (metric === 'weight_kg' || metric === 'muscle_mass' || metric === 'standard_weight') {
    return unit === 'imperial' ? kgToLb(v) : v
  }
  if (metric === 'waist_cm' || metric === 'height_cm' || metric === 'hip_cm' || metric === 'neck_cm'
    || metric === 'chest_cm' || metric === 'shoulder_cm' || metric === 'thigh_cm' || metric === 'arm_cm') {
    return unit === 'imperial' ? cmToIn(v) : v
  }
  return v
}

export function fmtNum(v: number | null | undefined, digits = 1): string {
  if (v == null || Number.isNaN(v)) return '--'
  return Number(v).toFixed(digits)
}

export function fmtDisp(unit: Unit, metric: string, v: number | null | undefined): string {
  const d = dispValue(unit, metric, v == null ? null : Number(v))
  return d == null ? '--' : fmtNum(d)
}

export function round1(v: number | null): number | null {
  return v == null ? null : Math.round(v * 10) / 10
}

export function cmField(unit: () => Unit, target: { value: number | null }) {
  return computed({
    get: () => (unit() === 'imperial' ? round1(cmToIn(target.value)) : target.value),
    set: (v: number | null | undefined) => {
      target.value = unit() === 'imperial' ? inToCm(v ?? null) : (v ?? null)
    },
  })
}

export function weightField(unit: () => Unit, target: { value: number | null }) {
  return computed({
    get: () => (unit() === 'imperial' ? round1(kgToLb(target.value)) : target.value),
    set: (v: number | null | undefined) => {
      target.value = unit() === 'imperial' ? lbToKg(v ?? null) : (v ?? null)
    },
  })
}
